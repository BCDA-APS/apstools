#!/bin/bash

# publish this package

## Define the release

STARTED=$(date)
PACKAGE=$(python setup.py --name)
RELEASE=$(python setup.py --version)
echo "# ($(date)) PACKAGE: ${PACKAGE}"
echo "# ($(date)) RELEASE: ${RELEASE}"

if [[ ${RELEASE} == *dirty || ${RELEASE} == *+* ]] ; then
  echo "# version: ${RELEASE} not ready to publish"
  exit 1
fi

echo "# ($(date)) - - - - - - - - - - - - - - - - - - - - - - build for PyPI"

## PyPI Build and upload::

echo "# ($(date)) Building for upload to PyPI"
python setup.py sdist bdist_wheel
echo "# ($(date)) Built for PyPI"

echo "# ($(date)) - - - - - - - - - - - - - - - - - - - - - - upload to PyPI"

twine upload "dist/${PACKAGE}-${RELEASE}*"
echo "# ($(date)) Uploaded to PyPI"

echo "# ($(date)) - - - - - - - - - - - - - - - - - - - - - - conda build"

## Conda Build and upload::

### Conda channels

if [[ ${RELEASE} == *rc* ]] ; then
  # anything else, such as: pre-release, release candidates, or testing purposes
  CHANNEL=aps-anl-dev
else
  # production releases
  CHANNEL=aps-anl-tag
fi
echo "# ($(date)) CHANNEL: ${CHANNEL}"

### publish (from linux)

echo "# ($(date)) Building for upload to conda"

export CONDA_BLD_PATH=/tmp/conda-bld
/bin/mkdir -p ${CONDA_BLD_PATH}

conda build ./conda-recipe/
echo "# ($(date)) Built for conda"

echo "# ($(date)) - - - - - - - - - - - - - - - - - - - - - - upload conda"

BUILD_DIR=${CONDA_BLD_PATH}/noarch
_package_=$(echo "${PACKAGE}" | tr '[:upper:]' '[:lower:]')
BUNDLE="${BUILD_DIR}/${_package_}-${RELEASE}-*_0.tar.bz2"
echo "# ($(date)) uploading to anaconda"
echo "# ($(date)) CHANNEL: ${CHANNEL}"
anaconda upload -u "${CHANNEL}" "${BUNDLE}"

# also post to my personal channel
anaconda upload "${BUNDLE}"
echo "# ($(date)) Uploaded to anaconda"

echo "# (${STARTED}) started publishing script"
echo "# ($(date)) finished publishing script"
