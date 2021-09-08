#! /bin/bash

#
# CK installation script
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2018;
#

# PACKAGE_DIR
# INSTALL_DIR

######################################################################################
# Check if has --system option
${CK_ENV_COMPILER_PYTHON_FILE} -m pip install --help > tmp-pip-help.tmp
if grep -q "\-\-system" tmp-pip-help.tmp ; then
 SYS=" --system"
fi
rm -f tmp-pip-help.tmp

######################################################################################
echo "Downloading and installing deps ..."
echo ""

INSTALL_PYTHON_LIBS="decorator tornado psutil wget"
if [ "${TVM_FPGA_SERVER}" != "ON" ] ; then
   INSTALL_PYTHON_LIBS="${PYTHON_LIBS} xgboost nose pylint numpy nose-timer cython scipy"
fi

EXTRA_PYTHON_SITE=${INSTALL_DIR}/src/python

${CK_ENV_COMPILER_PYTHON_FILE} -m pip install --ignore-installed ${INSTALL_PYTHON_LIBS} -t ${EXTRA_PYTHON_SITE} ${SYS}
if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

# Building TVM etc

cd ${INSTALL_DIR}
cd src

if [ "${TVM_FPGA_SERVER}" == "ON" ] ; then
  TVM_MAKE_TARGET=runtime
fi

mkdir build
cd build

# Update config.cmake
cp -f ${TMP_TVM_CMAKE_UPDATE_FILE} ../config.cmake
if [ "${?}" != "0" ] ; then
  echo "Error: config.cmake update failed!"
  exit 1
fi

rm -f ${TMP_TVM_CMAKE_UPDATE_FILE}

cmake ..
if [ "${?}" != "0" ] ; then
  echo "Error: cmake failed!"
  exit 1
fi

make ${TVM_MAKE_TARGET} -j ${CK_HOST_CPU_NUMBER_OF_PROCESSORS}
if [ "${?}" != "0" ] ; then
  echo "Error: make failed!"
  exit 1
fi

if [ "${USE_VTA_CONFIG}" != "" ] ; then
  cp -f ../vta/config/${USE_VTA_CONFIG} vta_config.json
fi

return 0
