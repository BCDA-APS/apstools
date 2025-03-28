#!/usr/bin/env bash

# Check if micromamba is available in system path or home directory
if ! command -v micromamba &> /dev/null; then
    if [ -f "$HOME/.local/bin/micromamba" ]; then
        export MAMBA_EXE="$HOME/.local/bin/micromamba"
        export MAMBA_ROOT_PREFIX="$HOME/micromamba"
        eval "$($MAMBA_EXE shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX")"
    else
        echo "Error: micromamba is not found in your system."
        exit 1
    fi
fi

# Check if podman is available
if ! command -v podman &> /dev/null; then
    echo "Error: podman is not found in your system."
    echo "Please install podman first:"
    echo "  sudo apt-get install podman"
    exit 1
fi

# Default values for test flags
RUN_MAIN=false
RUN_DEVICES=false
RUN_PLANS=false
RUN_UTILS=false
RUN_ALL=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --main)
            RUN_MAIN=true
            shift
            ;;
        --devices)
            RUN_DEVICES=true
            shift
            ;;
        --plans)
            RUN_PLANS=true
            shift
            ;;
        --utils)
            RUN_UTILS=true
            shift
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Valid options are: --main, --devices, --plans, --utils, --all"
            exit 1
            ;;
    esac
done

# If no options specified, default to main
if [ "$RUN_MAIN" = false ] && [ "$RUN_DEVICES" = false ] && [ "$RUN_PLANS" = false ] && [ "$RUN_UTILS" = false ] && [ "$RUN_ALL" = false ]; then
    RUN_MAIN=true
fi

MAIN_DIR=$(dirname $(readlink -f $0))/../../
ENV_NAME="bits_test1"
ENV_FILE="$MAIN_DIR/environment.yml"

echo "MAIN_DIR: $MAIN_DIR"
echo "ENV_FILE: $ENV_FILE"
echo "Running tests:"
[ "$RUN_MAIN" = true ] && echo "  - Main tests"
[ "$RUN_DEVICES" = true ] && echo "  - Device tests"
[ "$RUN_PLANS" = true ] && echo "  - Plan tests"
[ "$RUN_UTILS" = true ] && echo "  - Utility tests"
[ "$RUN_ALL" = true ] && echo "  - All tests with coverage"

cd $MAIN_DIR

# Create a temp environment name
ENV_NAME="bits_test1"
PYVER="3.11"

# Check if environment exists
if ! micromamba env list | grep -q "^$ENV_NAME "; then
    echo "Creating new environment $ENV_NAME..."
    # Create the environment
    micromamba create -y -n "$ENV_NAME" -f environment.yml python="$PYVER" \
    coveralls pytest pytest-cov setuptools-scm
else
    echo "Environment $ENV_NAME already exists, skipping creation..."
fi

# Activate the environment
eval "$(micromamba shell hook --shell=bash)"
micromamba activate "$ENV_NAME"

# Unpack
# Check if databroker-pack is installed
if ! pip list | grep -q "^databroker-pack "; then
    echo "Installing databroker-pack..."
    pip install databroker-pack
else
    echo "databroker-pack already installed, skipping..."
fi
cd resources
bash ./unpack.sh
python -c "import databroker; print(list(databroker.catalog)); print(databroker.catalog_search_path());"
cd ..


# show all available catalogs
databroker-pack --list


# -------------------------------
# Start EPICS IOCs in Podman
# -------------------------------
echo "Starting EPICS IOCs via Podman..."

# Create necessary directories
mkdir -p /tmp/docker_ioc/iocgp/tmp
mkdir -p /tmp/docker_ioc/iocad/tmp

# Start GP IOC
podman \
    run -it -d --rm \
    --name iocgp \
    -e "PREFIX=gp:" \
    --net=host \
    -v /tmp/docker_ioc/iocgp/tmp:/tmp \
    prjemian/synapps:latest \
    bash
podman exec iocgp bash /root/bin/gp.sh start

# Start ADSIM IOC
podman \
    run -it -d --rm \
    --name iocad \
    -e "PREFIX=ad:" \
    --net=host \
    -v /tmp/docker_ioc/iocad/tmp:/tmp \
    prjemian/synapps:latest \
    bash
podman exec iocad bash /root/bin/adsim.sh start

podman ps -a
ls -lAFgh /tmp/docker_ioc/iocad/
ls -lAFgh /tmp/docker_ioc/iocgp/

# -------------------------------
# Confirm EPICS IOC Availability via caget
# -------------------------------
echo "Confirming EPICS IOCs using caget..."
podman exec iocgp grep float1 /home/iocgp/dbl-all.txt
podman exec iocgp /opt/base/bin/linux-x86_64/caget gp:UPTIME gp:gp:float1
podman exec iocad /opt/base/bin/linux-x86_64/caget ad:cam1:Acquire_RBV
which caget
caget gp:UPTIME
caget gp:gp:float1
caget ad:cam1:Acquire_RBV

# -------------------------------
# Confirm EPICS IOC via PyEpics & ophyd
# -------------------------------
echo "Confirming EPICS IOC using PyEpics..."
python -c "import epics; print(epics.caget('gp:UPTIME'))"

echo "Confirming EPICS IOC using ophyd..."
python -c "import ophyd; up = ophyd.EpicsSignalRO('gp:UPTIME', name='up'); pv = ophyd.EpicsSignalRO('gp:gp:float1', name='pv'); up.wait_for_connection(); print(up.get(), pv.get())"

# -------------------------------
# Confirm Catalog Length
# -------------------------------
echo "Checking catalog length (expecting 53)..."
python -c "import databroker; print(len(databroker.catalog['apstools_test']))"

# -------------------------------
# Run Selected Tests
# -------------------------------
if [ "$RUN_ALL" = true ]; then
    echo "Running all tests with coverage..."
    coverage run --concurrency=thread --parallel-mode -m pytest -vvv --exitfirst .
    coverage combine
    coverage report --precision 3
else
    if [ "$RUN_MAIN" = true ]; then
        echo "Running main tests..."
        pytest -v ./apstools/tests
    fi
    
    if [ "$RUN_DEVICES" = true ]; then
        echo "Running device tests..."
        pytest -v ./apstools/devices/tests
        pytest -v ./apstools/synApps/tests
    fi
    
    if [ "$RUN_PLANS" = true ]; then
        echo "Running plan tests..."
        pytest -v ./apstools/plans/tests
    fi
    
    if [ "$RUN_UTILS" = true ]; then
        echo "Running utility tests..."
        pytest -v ./apstools/utils/tests
#        pytest -v ./apstools/migration/tests
    fi
fi

echo "All steps completed successfully!"