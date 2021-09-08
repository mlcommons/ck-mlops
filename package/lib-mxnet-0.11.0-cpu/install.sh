#! /bin/bash

# CK installation script for MXNet package
#
# Developer(s):
#  * Grigori Fursin, dividiti/cTuning foundation
#

# PACKAGE_DIR
# INSTALL_DIR

export MXNET_LIB_DIR=${INSTALL_DIR}/lib

echo ""
echo "Removing '${MXNET_LIB_DIR}' ..."
rm -rf ${MXNET_LIB_DIR}

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

######################################################################################
echo ""
echo "Downloading and installing MXNet prebuilt binaries ..."
echo ""

# FGG added --upgrade later to install correct numpy with mxnet
${CK_ENV_COMPILER_PYTHON_FILE} -m pip install mxnet${MXNET_EXTRA}==${MXNET_PACKAGE_VER} -t ${INSTALL_DIR}/lib ${SYS} --upgrade
if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

######################################################################################
echo ""
read -r -p "Install extra dependencies for classification using SUDO and apt-get (y/N)? " x

echo "XYZ=$x"

case "$x" in
  [yY][eE][sS]|[yY])
    echo ""
    echo "Using ${SUDO} ${CK_PYTHON_PIP_BIN_FULL} ..."
    echo ""

    echo ""
    echo "Installing python-tk (sudo) ..."
    echo ""

    if [ "${CK_PYTHON_VER3}" == "YES" ] ; then
      sudo apt-get install python3-tk
    else
      sudo apt-get install python-tk
    fi 
    ;;
esac


exit 0
