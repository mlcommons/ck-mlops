#!/bin/bash

#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Leo Gordon, 2019
#

# for example,
#   INSTALL_DIR     = "lib-armcl-viascons-linux-64"
#   PACKAGE_SUB_DIR = "src"

ARMCL_SOURCE_DIR=$INSTALL_DIR/$PACKAGE_SUB_DIR

# Configure target.
MACHINE=$(uname -m)
if [ "${MACHINE}" == "armv7l" ] || [ "${CK_TARGET_CPU_BITS}" == "32" ]; then
    ARCH="armv7a"
elif [ "${MACHINE}" == "aarch64" ]; then
    ARCH="arm64-v8a"
else
    ARCH="arm64-v8a"
    echo "Warning: Unknown machine type: ${MACHINE}."
fi

############################################################
echo ""
echo "Building ArmCL '${PACKAGE_VERSION}' in '${INSTALL_DIR}' using SCons with ${CK_HOST_CPU_NUMBER_OF_PROCESSORS:-UndefinedNumberOf} threads."
echo "Backends: USE_NEON='${USE_NEON}'; USE_OPENCL='${USE_OPENCL}'."
echo "Target: arch=${ARCH}."
echo ""

if [ "$USE_NEON" == "ON" ] || [ "$USE_NEON" == "on" ] || [ "$USE_NEON" == "YES" ] || [ "$USE_NEON" == "yes" ] || [ "$USE_NEON" == "1" ]
then
    ARMCL_SCONS_INTERNAL_NEON="neon=1"
else
    ARMCL_SCONS_INTERNAL_NEON=""
fi

if [ "$USE_OPENCL" == "ON" ] || [ "$USE_OPENCL" == "on" ] || [ "$USE_OPENCL" == "YES" ] || [ "$USE_OPENCL" == "yes" ] || [ "$USE_OPENCL" == "1" ]
then
    ARMCL_SCONS_INTERNAL_OPENCL="opencl=1 embed_kernels=1"
else
    ARMCL_SCONS_INTERNAL_OPENCL=""
fi


cd ${ARMCL_SOURCE_DIR}
CC=${CK_CC} CXX=${CK_CXX} scons -j ${CK_HOST_CPU_NUMBER_OF_PROCESSORS:-1} \
    arch=${ARCH} toolchain_prefix=" " \
    extra_cxx_flags="-fPIC" \
    debug=0 asserts=0 \
    benchmark_tests=0 \
    validation_tests=0 \
    ${ARMCL_SCONS_INTERNAL_NEON} ${ARMCL_SCONS_INTERNAL_OPENCL} \
    install_dir=${INSTALL_DIR}/install
