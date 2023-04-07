#!/bin/bash

# iocmgr.sh -- Manage IOCs in docker containers

# Usage: ${0} ACTION IOC PRE
# ACTION    console|restart|run|start|status|stop|caqtdm|medm|usage
# IOC       "gp", "adsim", (as provided by image)
# PRE       User's choice.  No trailing colon!

# make all arguments lower case
ACTION=$(echo "${1}" | tr '[:upper:]' '[:lower:]')
IOC=$(echo "${2}" | tr '[:upper:]' '[:lower:]')
PRE=$(echo "${3}" | tr '[:upper:]' '[:lower:]')

# -------------------------------------------

# docker image
IMAGE=prjemian/synapps:latest

# IOC prefix
if [ "${PRE:(-1)}" == ":" ]; then
    # remove the trailing colon
    PRE="${PRE:0:-1}"
fi
PREFIX=${PRE}:

# name of docker container
CONTAINER=ioc${PRE}

# pass the IOC PREFIX to the container at boot time
ENVIRONMENT="PREFIX=${PREFIX}"

# convenience definitions
RUN="docker exec ${CONTAINER}"
TMP_ROOT=/tmp/docker_ioc
HOST_IOC_ROOT=${TMP_ROOT}/${CONTAINER}
HOST_TMP_SHARE="${HOST_IOC_ROOT}/tmp"
IOC_SCRIPT="/root/bin/${IOC}.sh"

get_docker_container_process() {
    process=$(docker ps -a | grep ${CONTAINER})
}

get_docker_container_id() {
    get_docker_container_process
    cid=$(echo ${process} | head -n1 | awk '{print $1;}')
}

start_container(){
    echo -n "starting container '${CONTAINER}' with PREFIX='${PREFIX}' ... "
    docker \
        run -it -d --rm \
        --name "${CONTAINER}" \
        -e "${ENVIRONMENT}" \
        --net=host \
        -v "${HOST_TMP_SHARE}":/tmp \
        "${IMAGE}" \
        bash
}

start_ioc_in_container(){
    get_docker_container_process
    if [ "" != "${process}" ]; then
        docker exec "${CONTAINER}" bash "${IOC_SCRIPT}" start
    fi
}

restart(){
    get_docker_container_id
    if [ "" != "${cid}" ]; then
        stop
    fi
    start
}

status(){
    get_docker_container_process
    if [ "" == "${process}" ]; then
        echo "Not found: ${CONTAINER}"
    else
        echo "docker container status"
        echo "${process}"
        echo ""
        echo "processes in docker container"
        docker top "${CONTAINER}"
        echo ""
        echo "IOC status"
        docker exec "${CONTAINER}" bash "${IOC_SCRIPT}" status
    fi
}

start(){
    get_docker_container_process
    if [ "" != "${process}" ]; then
        echo "Found existing ${CONTAINER}, cannot start new one."
        echo "${process}"
    else
        start_container
        start_ioc_in_container
    fi
}

stop(){
    get_docker_container_id
    if [ "" != "${cid}" ]; then
        echo -n "stopping container '${CONTAINER}' ... "
        docker stop "${CONTAINER}"
        get_docker_container_id
        if [ "" != "${cid}" ]; then
            echo -n "removing container '${CONTAINER}' ... "
            docker rm ${CONTAINER}
        fi
    fi
}

symbols(){
    # for diagnostic purposes
    get_docker_container_id
    echo "cid=${cid}"
    echo "process=${process}"
    echo "ACTION=${ACTION}"
    echo "CONTAINER=${CONTAINER}"
    echo "ENVIRONMENT=${ENVIRONMENT}"
    echo "HOST_IOC_ROOT=${HOST_IOC_ROOT}"
    echo "HOST_TMP_SHARE=${HOST_TMP_SHARE}"
    echo "IMAGE=${IMAGE}"
    echo "IOC=${IOC}"
    echo "PRE=${PRE}"
    echo "PREFIX=${PREFIX}"
    echo "RUN=${RUN}"
    echo "TMP_ROOT=${TMP_ROOT}"
}

caqtdm(){
    if [ "gp" == "${IOC}" ]; then
        custom_screen="ioc${PRE}.ui"
    fi
    # echo "custom_screen=${custom_screen}"
    "${HOST_TMP_SHARE}/start_caQtDM_${PRE}" "${custom_screen}"
}

medm(){
    if [ "gp" == "${IOC}" ]; then
        custom_screen="ioc${PRE}.ui"
    fi
    "${HOST_TMP_SHARE}/start_MEDM_${PRE}" "${custom_screen}"
}

usage(){
    echo "Usage: ${0} ACTION IOC PRE"
    echo "  where:"
    echo "  ACTION  choices: start stop restart status caqtdm medm usage"
    echo "  IOC     choices: gp adsim"
    echo "  PRE     User's choice.  No trailing colon!"
    echo ""
    echo "Received: ${0} ${ACTION} ${IOC} ${PRE}"
    exit 1
}

# check the inputs
if [ "3" -ne "$#" ]; then
    usage
fi

case "${IOC}" in
    adsim)  ;;
    gp)  ;;
    *) usage
esac

case "${ACTION}" in
  start) start ;;
  stop) stop ;;
  restart) restart ;;
  status) status ;;
  symbols) symbols ;;
  caqtdm) caqtdm ;;
  medm) medm ;;
  *) usage
esac
