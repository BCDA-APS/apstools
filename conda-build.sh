#!/bin/bash

# builds conda packages for APS_BlueSky_tools
# based on latest PyPI release

# this script intended to be run ONLY from linux-64 host architecture

# all lower case (for conda build command below)
export PACKAGE=aps_bluesky_tools
export SANDBOX=/tmp/${PACKAGE}-sandbox

/bin/rm -rf ${SANDBOX}
mkdir -p ${SANDBOX}
cd ${SANDBOX}

export OUTPUT_DIR=./conda-packages
export RECIPE_DIR=./${PACKAGE}
export ANACONDA=${HOME}/Apps/anaconda
export BUILD_DIR=${ANACONDA}/conda-bld

/bin/rm -rf ${OUTPUT_DIR}
/bin/rm -rf ${RECIPE_DIR}
/bin/rm -rf ${BUILD_DIR}
/bin/rm -f build.log

conda skeleton pypi ${PACKAGE}

export BUILD_TARGETS=
#export BUILD_TARGETS+=" osx-64"
#export BUILD_TARGETS+=" win-32"
#export BUILD_TARGETS+=" win-64"
#export BUILD_TARGETS+=" linux-32"
#export BUILD_TARGETS+=" linux-64"

mkdir -p ${OUTPUT_DIR}/linux-64
touch build.log

export PYTHON_VERSIONS=
#export PYTHON_VERSIONS+=3.5
export PYTHON_VERSIONS+=3.6

for PY_VER in ${PYTHON_VERSIONS}; do
	echo "Building for Python ${PY_VER}"
	echo "# --- Python ${PY_VER} -------" >> build.log
	conda build --python ${PY_VER} ${RECIPE_DIR} 2>&1 >> build.log
	export BASE_FILE=`conda build --python ${PY_VER} ${RECIPE_DIR} --output`
	cp ${BASE_FILE} ${OUTPUT_DIR}/linux-64/
	for ARCH in ${BUILD_TARGETS}; do
	  conda convert --platform ${ARCH} ${BASE_FILE} -o ${OUTPUT_DIR}/
	done
done

anaconda upload --force ${OUTPUT_DIR}/*/*.bz2

cd ${HOME}
/bin/rm -rf ${SANDBOX}
/bin/rm -rf /tmp/{_,tmp}*
