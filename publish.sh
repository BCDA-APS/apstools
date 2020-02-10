#!/bin/bash

# publish this package

## Define the release

PACKAGE=`python setup.py --name`
RELEASE=`python setup.py --version`
echo "PACKAGE: ${PACKAGE}"
echo "RELEASE: ${RELEASE}"

if [[ ${RELEASE} == *dirty || ${RELEASE} == *+* ]] ; then
  echo "version: ${RELEASE} not ready to publish"
  exit 1
fi

echo "# - - - - - - - - - - - - - - - - - - - - - - - build & upload to PyPI"

## PyPI Build and upload::

echo "Building for upload to PyPI"
python setup.py sdist bdist_wheel
twine upload dist/${PACKAGE}-${RELEASE}*

echo "# - - - - - - - - - - - - - - - - - - - - - - - conda build"

## Conda Build and upload::

### Conda channels

if [[ ${RELEASE} == *rc* ]] ; then
  # anything else, such as: pre-release, release candidates, or testing purposes
  CHANNEL=aps-anl-dev
else
  # production releases
  CHANNEL=aps-anl-tag
fi
echo "CHANNEL: ${CHANNEL}"

### publish (from linux)

echo "Building for upload to conda"

export CONDA_BLD_PATH=/tmp/conda-bld
/bin/mkdir -p ${CONDA_BLD_PATH}

conda build ./conda-recipe/

echo "# - - - - - - - - - - - - - - - - - - - - - - - upload conda"

BUILD_DIR=${CONDA_BLD_PATH}/noarch
_package_=$(echo ${PACKAGE} | tr '[:upper:]' '[:lower:]')
BUNDLE=${BUILD_DIR}/${_package_}-${RELEASE}-*_0.tar.bz2
echo "upload to conda"
echo "CHANNEL: ${CHANNEL}"
anaconda upload -u ${CHANNEL} ${BUNDLE}

# also post to my personal channel
anaconda upload ${BUNDLE}
