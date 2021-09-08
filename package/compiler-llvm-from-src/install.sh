#! /bin/bash

# PACKAGE_DIR
# INSTALL_DIR

# Based on package:compiler-llvm-from-source

echo "******************************************************"
cd ${INSTALL_DIR}

if [ ! -d "llvm" ]; then
  git clone -b "${PACKAGE_GIT_CHECKOUT}" ${PACKAGE_GIT_LLVM} llvm
  if [ "${?}" != "0" ]; then exit 1; fi
fi

cd llvm

mkdir -p install
mkdir -p build

echo "******************************************************"
cd build
${CK_ENV_TOOL_CMAKE_BIN}/cmake .. \
    -DLLVM_ENABLE_PROJECTS=clang \
    -DCMAKE_CXX_COMPILER="${CK_CXX_PATH_FOR_CMAKE}" \
    -DCMAKE_CXX_FLAGS="${CK_CXX_FLAGS_FOR_CMAKE} ${EXTRA_FLAGS}" \
    -DCMAKE_C_COMPILER="${CK_CC_PATH_FOR_CMAKE}" \
    -DCMAKE_C_FLAGS="${CK_CC_FLAGS_FOR_CMAKE} ${EXTRA_FLAGS}" \
    -DCMAKE_AR="${CK_AR_PATH_FOR_CMAKE}" \
    -DCMAKE_LINKER="${CK_LD_PATH_FOR_CMAKE}" \
    -DCMAKE_RANLIB="${CK_RANLIB_PATH_FOR_CMAKE}" \
    -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}/install" \
    -DCMAKE_BUILD_TYPE=Release \
    -DLLVM_ENABLE_RTTI=ON \
    -DLLVM_INSTALL_UTILS=ON \
    ../llvm/
if [ "${?}" != "0" ]; then exit 1; fi

echo "******************************************************"
cmake --build . --target install -j${CK_HOST_CPU_NUMBER_OF_PROCESSORS}
if [ "${?}" != "0" ]; then exit 1; fi

# Clean build directory (too large)
cd ${INSTALL_DIR}
rm -rf build

echo "******************************************************"
echo "LLVM was built and installed to ${INSTALL_DIR}/install ..."
