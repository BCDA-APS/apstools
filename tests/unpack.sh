#!/bin/bash

# file: unpack.sh
# purpose: unpack databroker test data

CAT+=" apstools_test"
CAT+=" usaxs_test"
TMP=/tmp
SRC=$(dirname $(readlink -f $0))

# cd ${TMP}
for c in ${CAT}; do
    echo ${SRC}/${c}.zip
    unzip -u ${SRC}/${c}.zip -d ${TMP}
    databroker-unpack inplace  ${TMP}/${c}   ${c}
done
