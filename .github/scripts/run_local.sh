#!/usr/bin/env bash
set -vxeuo pipefail


MAIN_DIR=$(dirname $(readlink -f $0))/../../
ENV_NAME="bits_test1"
ENV_FILE="$MAIN_DIR/environment.yml"
IOC_MGR_SCRIPT="$MAIN_DIR/.github/scripts/iocmgr.sh"

echo "MAIN_DIR: $MAIN_DIR"
echo "ENV_FILE: $ENV_FILE"
echo "IOC_MGR_SCRIPT: $IOC_MGR_SCRIPT"

cd $MAIN_DIR

# Create a temp environment name
ENV_NAME="bits_test1"
PYVER="3.11"

# Create the environment
micromamba create -y -n "$ENV_NAME" -f environment.yml python="$PYVER" \
coveralls pytest pytest-cov setuptools-scm

# Activate the environment
eval "$(micromamba shell hook --shell=bash)"
micromamba activate "$ENV_NAME"

# Unpack
pip install databroker-pack
cd resources
bash ./unpack.sh
python -c "import databroker; print(list(databroker.catalog)); print(databroker.catalog_search_path());"
cd ..


# show all available catalogs
databroker-pack --list


# -------------------------------
# Start EPICS IOCs in Docker
# -------------------------------
echo "Starting EPICS IOCs via Docker..."
bash $IOC_MGR_SCRIPT start GP gp
bash $IOC_MGR_SCRIPT start ADSIM ad
docker ps -a
ls -lAFgh /tmp/docker_ioc/iocad/
ls -lAFgh /tmp/docker_ioc/iocgp/

# -------------------------------
# Confirm EPICS IOC Availability via caget
# -------------------------------
echo "Confirming EPICS IOCs using caget..."
docker exec iocgp grep float1 /home/iocgp/dbl-all.txt
docker exec iocgp /opt/base/bin/linux-x86_64/caget gp:UPTIME gp:gp:float1
docker exec iocad /opt/base/bin/linux-x86_64/caget ad:cam1:Acquire_RBV
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
# Run Tests with Pytest and Coverage
# -------------------------------
# echo "Running tests with pytest and generating coverage report..."
# coverage run --concurrency=thread --parallel-mode -m pytest -vvv --exitfirst .
# coverage combine
# coverage report --precision 3


pytest -v ./apstools/tests
pytest -v ./apstools/devices/tests
pytest -v ./apstools/plans/tests
pytest -v ./apstools/utils/tests

echo "All steps completed successfully!"