#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2015;
# - Anton Lokhmotov, 2016.
#

# PACKAGE_DIR
# INSTALL_DIR

echo "**************************************************************"
echo "Preparing vars for MxNet ..."

# Check extra stuff
export MXNET_LIB_DIR=${INSTALL_DIR}/lib

echo ""
echo "Removing '${MXNET_LIB_DIR}' ..."
rm -rf ${MXNET_LIB_DIR}

EXTRA_MAKE_FLAGS=""
if [ "${USE_F16C}" != "" ] ; then
   EXTRA_MAKE_FLAGS="${EXTRA_MAKE_FLAGS} USE_F16C=${USE_F16C}"
fi

cd ${INSTALL_DIR}/src

make ${CK_MAKE_BEFORE} -j ${CK_HOST_CPU_NUMBER_OF_PROCESSORS} USE_OPENCV=${USE_OPENCV} \
     USE_BLAS=${USE_BLAS} \
     USE_LAPACK=${USE_LAPACK} USE_LAPACK_PATH=${CK_ENV_LIB_LAPACK_LIB} \
     ${EXTRA_MAKE_FLAGS}

if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

######################################################################################
# Print info about possible issues
echo ""
echo "Note that you sometimes need to upgrade your pip to the latest version"
echo "to avoid well-known issues with user/system space installation:"

SUDO="sudo "
if [[ ${CK_PYTHON_PIP_BIN_FULL} == /home/* ]] ; then
  SUDO=""
fi

######################################################################################
# Check if has --system option
${CK_ENV_COMPILER_PYTHON_FILE} -m pip install --help > tmp-pip-help.tmp
if grep -q "\-\-system" tmp-pip-help.tmp ; then
 SYS=" --system"
fi
rm -f tmp-pip-help.tmp

######################################################################################
echo "Downloading and installing Python deps ..."
echo ""

EXTRA_PYTHON_SITE=${INSTALL_DIR}/lib
mkdir -p ${EXTRA_PYTHON_SITE}

${CK_ENV_COMPILER_PYTHON_FILE} -m pip install --ignore-installed decorator wget matplotlib jupyter -t ${EXTRA_PYTHON_SITE}  ${SYS}
if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

if [ "${USE_OPENCV}" == "1" ] ; then
  ${CK_ENV_COMPILER_PYTHON_FILE} -m pip install --ignore-installed opencv-python -t ${EXTRA_PYTHON_SITE}  ${SYS}
  if [ "${?}" != "0" ] ; then
    echo "Error: installation failed!"
    exit 1
  fi
fi

return 0
