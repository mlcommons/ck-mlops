#! /bin/bash

#
# Installation script for DeePhi Technologies' Deep Neural Network Development Kit.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Flavio Vella, dividiti, 2018.
# - Anton Lokhmotov, dividiti 2018.
#

# PACKAGE_DIR
# INSTALL_DIR

echo "********************************************************************************"
echo "Installing DeePhi DNNDK from archive..."
echo ""

# Only installation from archive is supported.
if [ "${CK_DNNDK_ARCHIVE}" = "YES" ] && [ ! -f "${CK_DNNDK_ARCHIVE_PATH}" ]; then
    echo "Usage: ck install package --tags=lib,dnndk --env.CK_DNNDK_ARCHIVE_PATH=deephi-dnndk-<version>.tar.gz"
    exit 1
fi

# Extract archive.
echo "[DNNDK ARCHIVE]"
echo ${CK_DNNDK_ARCHIVE_PATH}

echo "Extracting '${CK_DNNDK_ARCHIVE_PATH}' to '${INSTALL_DIR}' ..."
cd ${INSTALL_DIR}
tar xvzf ${CK_DNNDK_ARCHIVE_PATH} --directory ${INSTALL_DIR} --strip-components=1
if [ "${?}" != "0" ] ; then
    echo "Error: extracting archive failed!"
    exit 1
fi
echo

# Get Ubuntu version.
echo "[SYSTEM VERSION]"
SYS_VERS=`lsb_release -a 2>/dev/null | sed -n '2p' `
echo ${SYS_VERS}
SYS_VERS=`echo ${SYS_VERS} | awk '{print $3}' | awk -F. '{print $1"."$2}' `
echo ${SYS_VERS}
echo

# Get CUDA version.
echo "[CUDA VERSION]"
CUDA_VERS=`cat ${CK_ENV_COMPILER_CUDA}/version.txt |  awk '{ print $3 } '`
CUDA_VERS=`echo ${CUDA_VERS} | awk -F. '{print $1"."$2}'`
echo ${CUDA_VERS}
echo

# Get cuDNN version.
echo "[CUDNN VERSION]"
CUDA_LIB_DNN_VERS=`cat ${CK_ENV_LIB_CUDNN_INCLUDE}/${CK_ENV_LIB_CUDNN_INCLUDE_NAME} | grep CUDNN_MAJOR -A 2 | head -3 | awk '{ver=ver$3"."}END{print ver}'`
CUDA_LIB_DNN_VERS=`echo ${CUDA_LIB_DNN_VERS} | awk -F. '{print $1"."$2"."$3}'`
echo ${CUDA_LIB_DNN_VERS}
echo

array=(
    ubuntu14.04/cuda_8.0.61_GA2_cudnn_v7.0.5
    ubuntu16.04/cuda_8.0.61_GA2_cudnn_v7.0.5
    ubuntu16.04/cuda_9.0_cudnn_v7.0.5
    ubuntu16.04/cuda_9.1_cudnn_v7.0.5
)
for data in ${array[@]}
do
    if [[ $data =~ ${SYS_VERS} ]] && [[ $data =~ ${CUDA_VERS} ]] && [[ $data =~ ${CUDA_LIB_DNN_VERS} ]] ; then
        BIN_DIR=${INSTALL_DIR}/bin
        echo  "Installing 'decent' to '${BIN_DIR}' ..."
        rm -rf ${BIN_DIR} && mkdir ${BIN_DIR}
        ln -s ${INSTALL_DIR}/host_x86/pkgs/${data}/decent ${BIN_DIR}/decent
        ln -s ${INSTALL_DIR}/host_x86/pkgs/${data}/dnnc-dpu${CK_DNNDK_DPU_VER} ${BIN_DIR}/dnnc
        chmod u+x ${BIN_DIR}/*
        if [ "${?}" != "0" ] ; then
            echo "Error: installation failed!"
            exit 1
        fi
        echo
        echo "Installation successful!"
        exit
    fi
done
