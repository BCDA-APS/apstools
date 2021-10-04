#!/bin/bash

# start an EPICS areaDetector ADSimDetector IOC in a docker container
#
# usage:  ./start_adsim.sh [PRE]
#   where PRE is the IOC prefix (without any trailing colon)
#   default:  PRE=13SIM1
#
# from: https://github.com/prjemian/epics-docker/blob/main/v1.1/n6_custom_areaDetector/start_adsim.sh

PRE=${1:-13SIM1}
IMAGE_SHORT_NAME=custom-synapps-6.2-ad-3.10

# -------------------------------------------
# IOC prefix
PREFIX=${PRE}:

# name of docker container
CONTAINER=ioc${PRE}

# name of docker image
IMAGE=prjemian/${IMAGE_SHORT_NAME}:latest

# name of IOC manager (start, stop, status, ...)
IOC_MANAGER=/opt/iocSimDetector/adsim.sh

# pass the IOC PREFIX to the container at boot time
ENVIRONMENT="PREFIX=${PREFIX}"

# convenience definitions
RUN="docker exec ${CONTAINER}"
TMP_ROOT=/tmp/docker_ioc
HOST_IOC_ROOT=${TMP_ROOT}/${CONTAINER}
IOC_TOP=${HOST_IOC_ROOT}/iocSimDetector
OP_DIR=${TMP_ROOT}/${IMAGE_SHORT_NAME}
HOST_TMP_SHARE=${HOST_IOC_ROOT}/tmp
# -------------------------------------------

# stop and remove container if it exists
remove_container.sh ${CONTAINER}

mkdir -p ${HOST_TMP_SHARE}

echo -n "starting container ${CONTAINER} ... "
docker run -d -it --rm --net=host \
    --name ${CONTAINER} \
    -e "${ENVIRONMENT}" \
    -v "${HOST_TMP_SHARE}":/tmp \
    ${IMAGE} \
    bash

sleep 1

echo -n "starting IOC ${CONTAINER} ... "
CMD="${RUN} ${IOC_MANAGER} start"
echo ${CMD}
${CMD}
sleep 2

# copy container's files to /tmp for medm & caQtDM
echo "copy IOC ${CONTAINER} to ${HOST_IOC_ROOT}"
docker cp ${CONTAINER}:/opt/iocSimDetector/  ${HOST_IOC_ROOT}
mkdir -p ${OP_DIR}
docker cp ${CONTAINER}:/opt/screens/   ${OP_DIR}

# edit files in docker container IOC for use with GUI software
echo "changing 13SIM1: to ${PREFIX} in ${CONTAINER}"
sed -i s+13SIM1+`echo ${PRE}`+g ${IOC_TOP}/start_caQtDM_adsim
sed -i s+_IOC_SCREEN_DIR_+`echo ${IOC_TOP}`+g ${IOC_TOP}/start_caQtDM_adsim
sed -i s+_AD_SCREENS_DIR_+`echo ${OP_DIR}/screens/ui`+g ${IOC_TOP}/start_caQtDM_adsim
sed -i s+"# CAQTDM_DISPLAY_PATH"+CAQTDM_DISPLAY_PATH+g ${IOC_TOP}/start_caQtDM_adsim

# TODO: find the caQtDM plugins and copy locally
# TODO: edit QT_PLUGIN_PATH in start_caQtDM_adsim
