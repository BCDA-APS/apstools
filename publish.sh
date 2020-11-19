#!/bin/bash

# publish this package
# Run this from the package's root directory.

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

find "dist" -name "${PACKAGE}-${RELEASE}*" | while read file
do
    echo "# ($(date)) upload: dist/${file}"
    twine upload "${file}"
done
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

echo "# ($(date)) uploading to anaconda"
echo "# ($(date)) CHANNEL: ${CHANNEL}"
find "${BUILD_DIR}" -name "${_package_}-${RELEASE}*.tar.bz2" | while read file
do
    echo "# ($(date)) upload: ${BUILD_DIR}/${file}"
    # to public channel
    anaconda upload -u "${CHANNEL}" "${file}"
    # to personal channel
    anaconda upload "${file}"
done
echo "# ($(date)) Uploaded to anaconda"

echo "# (${STARTED}) started publishing script"
echo "# ($(date)) finished publishing script"
