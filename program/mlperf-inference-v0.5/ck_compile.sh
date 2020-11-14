#!/bin/bash

BLD_DIR=${PWD}
SRC_DIR=../ov_mlperf_cpu/

# Configure.
${CK_ENV_TOOL_CMAKE_BIN}/${CK_CMAKE} ${CK_VERBOSE:-"--verbose=1"} \
-DCMAKE_C_COMPILER="${CK_CC_FULL_PATH}"              \
-DCMAKE_C_FLAGS="${CK_CC_FLAGS} ${EXTRA_FLAGS}"      \
-DCMAKE_CXX_COMPILER="${CK_CXX_FULL_PATH}"           \
-DCMAKE_CXX_FLAGS="${CK_CXX_FLAGS} ${EXTRA_FLAGS}"   \
-DCMAKE_AR="${CK_AR}"                                \
-DCMAKE_RANLIB="${CK_RANLIB}"                        \
-DCMAKE_LINKER="${CK_LD}"                            \
-DBOOST_DIR="${CK_ENV_LIB_BOOST}"                    \
-DOPENCV_DIR="${CK_ENV_LIB_OPENCV}"                  \
-DLOADGEN_DIR="${CK_ENV_LIB_MLPERF_LOADGEN_INCLUDE}" \
-DLOADGEN_LIB_DIR="${CK_ENV_LIB_MLPERF_LOADGEN_LIB}" \
-DOPENVINO_DIR="${CK_ENV_LIB_OPENVINO}"              \
-DOPENVINO_VER="${CK_ENV_LIB_OPENVINO_VERSION}"      \
-DBUILD_DIR=${BLD_DIR} \
${SRC_DIR}
err=$?; if [ $err != 0 ]; then exit $err; fi

# Build.
make VERBOSE=1
err=$?; if [ $err != 0 ]; then exit $err; fi

exit 0
