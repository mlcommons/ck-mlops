#!/bin/bash

#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Leo Gordon, 2019
# - Anton Lokhmotov, 2019
#

################ Global: #############################################

ARMNN_SOURCE_DIR=$INSTALL_DIR/$PACKAGE_SUB_DIR
ARMNN_BUILD_DIR=$INSTALL_DIR/obj
export ARMNN_TARGET_DIR=$INSTALL_DIR/install

TF_PB_DIR=$INSTALL_DIR/generated_tf_pb_files
ONNX_SRC_DIR=$INSTALL_DIR/onnx

function exit_if_error() {
    if [ "${?}" != "0" ]; then exit 1; fi
}

echo ""
echo "Building ArmNN '${PACKAGE_VERSION}' in '${INSTALL_DIR}'."
echo "Frontends: USE_TF='${USE_TF}'; USE_TFLITE='${USE_TFLITE}'; USE_ONNX='${USE_ONNX}'."
echo "Backends: USE_NEON='${USE_NEON}'; USE_OPENCL='${USE_OPENCL}'"
echo ""

################ Frontend: ###########################################

if [ "$USE_TFLITE" == "YES" ] || [ "$USE_TFLITE" == "yes" ] || [ "$USE_TFLITE" == "ON" ] || [ "$USE_TFLITE" == "on" ] || [ "$USE_TFLITE" == "1" ]
then
    CMAKE_FOR_TFLITE=" -DBUILD_TF_LITE_PARSER=1 -DTF_LITE_GENERATED_PATH=${CK_ENV_LIB_TF_SRC_SRC}/tensorflow/lite/schema -DFLATBUFFERS_ROOT=${CK_ENV_LIB_FLATBUFFERS} -DFLATBUFFERS_LIBRARY=${CK_ENV_LIB_FLATBUFFERS_LIB}/libflatbuffers.a "
else
    CMAKE_FOR_TFLITE=""
fi

if [ -n "$CMAKE_FOR_TFLITE" ] || [ "$USE_TF" == "YES" ] || [ "$USE_TF" == "yes" ] || [ "$USE_TF" == "ON" ] || [ "$USE_TF" == "on" ] || [ "$USE_TF" == "1" ]
then
    echo ""
    echo "Generating Protobuf files from Tensorflow ..."
    echo ""

    rm -rf "${TF_PB_DIR}"
    mkdir ${TF_PB_DIR}
    cd ${CK_ENV_LIB_TF_SRC_SRC}
    ${ARMNN_SOURCE_DIR}/scripts/generate_tensorflow_protobuf.sh ${TF_PB_DIR} ${CK_ENV_LIB_PROTOBUF_HOST}
    exit_if_error

    CMAKE_FOR_TF=" -DBUILD_TF_PARSER=1 -DTF_GENERATED_SOURCES=${TF_PB_DIR} "
else
    CMAKE_FOR_TF=""
fi

if [ "$USE_ONNX" == "YES" ] || [ "$USE_ONNX" == "yes" ] || [ "$USE_ONNX" == "ON" ] || [ "$USE_ONNX" == "on" ] || [ "$USE_ONNX" == "1" ]
then
    echo ""
    echo "Generating Protobuf files from ONNX ..."
    echo ""

    rm -rf "${ONNX_SRC_DIR}"
    export ONNX_ML=1            #To clone ONNX with its ML extension
    git clone ${ONNX_BRANCH} --recursive ${ONNX_SRC_URL} ${ONNX_SRC_DIR}
    unset ONNX_ML
    cd ${ONNX_SRC_DIR}
    ${CK_ENV_LIB_PROTOBUF_HOST_BIN}/protoc onnx/onnx.proto --proto_path=. --proto_path=${CK_ENV_LIB_PROTOBUF_HOST_INCLUDE} --cpp_out ${ONNX_SRC_DIR}
    exit_if_error

    CMAKE_FOR_ONNX=" -DBUILD_ONNX_PARSER=1 -DONNX_GENERATED_SOURCES=${ONNX_SRC_DIR} "
else
    CMAKE_FOR_ONNX=""
fi

################ Backend: ############################################

if [ "$USE_NEON" == "YES" ] || [ "$USE_NEON" == "yes" ] || [ "$USE_NEON" == "ON" ] || [ "$USE_NEON" == "on" ] || [ "$USE_NEON" == "1" ]
then
    CMAKE_FOR_NEON=" -DARMCOMPUTENEON=1 "
else
    CMAKE_FOR_NEON=""
fi

if [ "$USE_OPENCL" == "YES" ] || [ "$USE_OPENCL" == "yes" ] || [ "$USE_OPENCL" == "ON" ] || [ "$USE_OPENCL" == "on" ] || [ "$USE_OPENCL" == "1" ]
then
    CMAKE_FOR_OPENCL=" -DARMCOMPUTECL=1 "
else
    CMAKE_FOR_OPENCL=""
fi

################ Default for Android is "NO": #######################

if [ "$CK_ARMNN_BUILD_TESTS" == "" ]
then
    CK_ARMNN_BUILD_TESTS="NO"
fi

############################################################
echo ""
echo "Running cmake for ArmNN ..."
echo ""

rm -rf "${ARMNN_BUILD_DIR}"
mkdir ${ARMNN_BUILD_DIR}
cd ${ARMNN_BUILD_DIR}


# Why we need DBOOST_LOG_DYN_LINK:
#       https://stackoverflow.com/questions/23137637/linker-error-while-linking-boost-log-tutorial-undefined-references

${CK_ENV_TOOL_CMAKE_BIN}/cmake ${ARMNN_SOURCE_DIR} \
    -DCMAKE_CROSSCOMPILING=YES \
    -DCMAKE_SYSTEM_NAME=Android \
    -DCMAKE_ANDROID_API=${CK_ANDROID_API_LEVEL} \
    -DCMAKE_ANDROID_ARCH_ABI=${CK_ANDROID_ABI} \
    -DCMAKE_ANDROID_STANDALONE_TOOLCHAIN=${CK_ENV_STANDALONE_TOOLCHAIN_ROOT} \
    -DCMAKE_CXX_FLAGS="-fPIE -fPIC -DBOOST_LOG_DYN_LINK=1" \
    -DCMAKE_EXE_LINKER_FLAGS="-pie -llog" \
    -DCMAKE_EXE_LINKER_FLAGS="${CK_LINKER_FLAGS_ANDROID_TYPICAL}  ${CK_COMPILER_FLAG_PTHREAD_LIB}" \
    -DCMAKE_INSTALL_PREFIX:PATH="${ARMNN_TARGET_DIR}" \
    -DARMCOMPUTE_ROOT=${CK_ENV_LIB_ARMCL_SRC} \
    -DARMCOMPUTE_BUILD_DIR=${CK_ENV_LIB_ARMCL_SRC}/build \
    -DBOOST_ROOT=${CK_ENV_LIB_BOOST} \
    -DBoost_NO_BOOST_CMAKE=NO \
    -DPROTOBUF_ROOT=${CK_ENV_LIB_PROTOBUF} \
    ${CMAKE_FOR_TF} ${CMAKE_FOR_TFLITE} ${CMAKE_FOR_ONNX} \
    ${CMAKE_FOR_NEON} ${CMAKE_FOR_OPENCL} \
    -DBUILD_UNIT_TESTS=${CK_ARMNN_BUILD_TESTS} \
    -DCMAKE_VERBOSE_MAKEFILE=NO         # very useful to flip over when debugging!

