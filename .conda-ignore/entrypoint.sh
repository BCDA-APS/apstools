#!/bin/bash

set -ex
set -o pipefail

go_to_build_dir() {
    if [ ! -z $INPUT_SUBDIR ]; then
        cd $INPUT_SUBDIR
    fi
}

check_if_meta_yaml_file_exists() {
    if [ ! -f meta.yaml ]; then
        echo "meta.yaml must exist in the directory that is being packaged and published."
        exit 1
    fi
}

build_and_test_package(){
    if  [ ${INPUT_TEST_ALL} = true ]; then
        eval conda build "-c "${INPUT_CHANNELS} --output-folder . .
    else
        # builds and tests one package, with the specified combination of python and numpy
        eval conda build "-c "${INPUT_CHANNELS} "--python="${INPUT_TEST_PYVER} "--numpy="${INPUT_TEST_NPVER} --output-folder . .
    fi

    if [ ${INPUT_CONVERT_OSX} = true ]; then
        conda convert -p osx-64 linux-64/*.tar.bz2
    fi
    if [ ${INPUT_CONVERT_WIN} = true ]; then
        conda convert -p win-64 linux-64/*.tar.bz2
    fi
}

upload_package(){
    # upload package if INPUT_PUBLISH is set to true
    if [ ${INPUT_PUBLISH} = true ]; then
        export ANACONDA_API_TOKEN=$INPUT_ANACONDATOKEN
        anaconda upload --label main noarch/*.tar.bz2 || anaconda upload --label main linux-64/*.tar.bz2
        if [ ${INPUT_CONVERT_OSX} = true ]; then
            if [ ${INPUT_TEST_ALL} = false ]; then
                conda convert -p osx-64 linux-64/*.tar.bz2
            fi
            anaconda upload --label main osx-64/*.tar.bz2
        fi
        if [ ${INPUT_CONVERT_WIN} = true ]; then
            if [ ${INPUT_TEST_ALL} = false ]; then
                conda convert -p win-64 linux-64/*.tar.bz2
            fi
            anaconda upload --label main win-64/*.tar.bz2
        fi
    fi
}

go_to_build_dir
check_if_meta_yaml_file_exists
build_and_test_package
upload_package
