#!/bin/bash

# publish this package

## Define the release

PACKAGE=apstools
RELEASE=`python setup.py --version`

## PyPI Build and upload::

python setup.py sdist bdist_wheel
twine upload dist/${PACKAGE}-${RELEASE}*

## Conda Build and upload::

### Conda channels

# `aps-anl-tag` production releases
# `aps-anl-dev` anything else, such as: pre-release, release candidates, or testing purposes
CHANNEL=aps-anl-tag

### publish

conda build ./conda-recipe/
CONDA_BASE=$(dirname $(dirname `which anaconda`))
BUILD_DIR=${CONDA_BASE}/conda-bld/noarch
anaconda upload -u ${CHANNEL} ${BUILD_DIR}/${PACKAGE}-${RELEASE}-py_0.tar.bz2
