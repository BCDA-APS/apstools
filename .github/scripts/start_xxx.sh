#!/bin/bash

# start a synApps XXX IOC in a docker container
#
# usage:  ./start_xxx.sh [PRE]
#   where PRE is the IOC prefix (without any trailing colon)
#   default:  PRE=xxx
#
# from: https://github.com/prjemian/epics-docker/blob/main/v1.1/n5_custom_synApps/start_xxx.sh

PRE=${1:-xxx}
IMAGE_SHORT_NAME=custom-synapps-6.2
XXX=xxx-R6-2

# -------------------------------------------
# IOC prefix
PREFIX=${PRE}:

# name of docker container
CONTAINER=ioc${PRE}

# name of docker image
IMAGE=prjemian/${IMAGE_SHORT_NAME}:latest

# name of IOC manager (start, stop, status, ...)
IOC_MANAGER=iocxxx/softioc/xxx.sh

# pass the IOC PREFIX to the container at boot time
ENVIRONMENT="PREFIX=${PREFIX}"

# convenience definitions
RUN="docker exec ${CONTAINER}"
TMP_ROOT=/tmp/docker_ioc
HOST_IOC_ROOT=${TMP_ROOT}/${CONTAINER}
IOC_TOP=${HOST_IOC_ROOT}/${XXX}
OP_DIR=${TMP_ROOT}/${IMAGE_SHORT_NAME}
HOST_TMP_SHARE=${HOST_IOC_ROOT}/tmp
# HOST_OPT_SHARE=${HOST_IOC_ROOT}/opt
# -------------------------------------------

# stop and remove container if it exists
remove_container.sh ${CONTAINER}

mkdir -p ${HOST_TMP_SHARE}
# mkdir -p ${HOST_OPT_SHARE}

echo -n "starting container ${CONTAINER} ... "
docker run -d -it --rm --net=host \
    --name ${CONTAINER} \
    -e "${ENVIRONMENT}" \
    -v "${HOST_TMP_SHARE}":/tmp \
    ${IMAGE} \
    bash
    # -v "${HOST_OPT_SHARE}":/opt \

sleep 1

# edit files in docker IOC for use with GUI software
echo "changing xxx: to ${PREFIX} in ${CONTAINER}"
CMD="${RUN} sed -i s:/APSshare/bin/caQtDM:caQtDM:g iocxxx/../../start_caQtDM_xxx"; ${CMD}
CMD="${RUN} sed -i s/xxx:/${PREFIX}/g iocxxx/../../xxxApp/op/adl/xxx.adl"; ${CMD}
CMD="${RUN} sed -i s/ioc=xxx/ioc=${PRE}/g iocxxx/../../xxxApp/op/adl/xxx.adl"; ${CMD}
CMD="${RUN} sed -i s/XXX/`echo ${PREFIX}`/g iocxxx/../../xxxApp/op/ui/xxx.ui"; ${CMD}
CMD="${RUN} sed -i s/xxx:/${PREFIX}/g iocxxx/../../xxxApp/op/ui/xxx.ui"; ${CMD}
CMD="${RUN} sed -i s/ioc=xxx/ioc=${PRE}/g iocxxx/../../xxxApp/op/ui/xxx.ui"; ${CMD}

echo -n "starting IOC ${CONTAINER} ... "
CMD="${RUN} ${IOC_MANAGER} start"
echo ${CMD}
${CMD}
sleep 2

# copy container's files to /tmp for medm & caQtDM
echo "copy IOC ${CONTAINER} to ${HOST_IOC_ROOT}"
docker cp ${CONTAINER}:/opt/synApps/support/${XXX}/  ${HOST_IOC_ROOT}
mkdir -p ${OP_DIR}
docker cp "${CONTAINER}:/opt/screens/"   ${OP_DIR}

# best to define these find/replace steps in pieces
# adjust the starter for caQtDM
FIND="source \${EPICS_APP}/setup_epics_common caqtdm"
# interpret the macros in the next string
REPLACE=`echo "export CAQTDM_DISPLAY_PATH=${IOC_TOP}/xxxApp/op/ui:${OP_DIR}/screens/ui"`
sed -i s+"${FIND}"+"${REPLACE}"+g ${IOC_TOP}/start_caQtDM_xxx

# adjust the starter for MEDM
FIND="source \${EPICS_APP}/setup_epics_common medm"
REPLACE=`echo "export EPICS_DISPLAY_PATH=${IOC_TOP}/xxxApp/op/adl:${OP_DIR}/screens/adl"`
sed -i s+"${FIND}"+"${REPLACE}"+g ${IOC_TOP}/start_MEDM_xxx
