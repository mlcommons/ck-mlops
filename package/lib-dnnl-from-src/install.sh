#! /bin/bash

# PACKAGE_DIR
# INSTALL_DIR

echo "******************************************************"
cd ${INSTALL_DIR}

if [ ! -d "src" ]; then
  git clone -b "${PACKAGE_GIT_CHECKOUT}" ${PACKAGE_GIT} src
  if [ "${?}" != "0" ]; then exit 1; fi
fi

mkdir -p install
mkdir -p build

echo "******************************************************"
cd build
${CK_ENV_TOOL_CMAKE_BIN}/cmake .. \
    -DCMAKE_CXX_COMPILER="${CK_CXX_PATH_FOR_CMAKE}" \
    -DCMAKE_CXX_FLAGS="${CK_CXX_FLAGS_FOR_CMAKE} ${EXTRA_FLAGS}" \
    -DCMAKE_C_COMPILER="${CK_CC_PATH_FOR_CMAKE}" \
    -DCMAKE_C_FLAGS="${CK_CC_FLAGS_FOR_CMAKE} ${EXTRA_FLAGS}" \
    -DCMAKE_AR="${CK_AR_PATH_FOR_CMAKE}" \
    -DCMAKE_LINKER="${CK_LD_PATH_FOR_CMAKE}" \
    -DCMAKE_RANLIB="${CK_RANLIB_PATH_FOR_CMAKE}" \
    -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}/install" \
    -DCMAKE_BUILD_TYPE=Release \
    -DDNNL_BUILD_TESTS=${DNNL_BUILD_TESTS} \
    -DDNNL_BUILD_EXAMPLES=${DNNL_BUILD_EXAMPLES} \
    -DDNNL_CPU_RUNTIME=${DNNL_CPU_RUNTIME} \
    ../src/
if [ "${?}" != "0" ]; then exit 1; fi

echo "******************************************************"
cmake --build . -j${CK_HOST_CPU_NUMBER_OF_PROCESSORS}
if [ "${?}" != "0" ]; then exit 1; fi

echo "******************************************************"
cmake --install .
if [ "${?}" != "0" ]; then exit 1; fi


# Clean build directory (too large)
cd ${INSTALL_DIR}
rm -rf build

echo "******************************************************"
echo "LLVM was built and installed to ${INSTALL_DIR}/install ..."
