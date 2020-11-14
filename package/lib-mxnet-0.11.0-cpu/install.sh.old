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

echo ""
read -r -p "Install OpenCV and other dependencies via sudo apt-get and pip (Y/n)? " x

case "$x" in
  [nN][oO]|[nN])
    ;;
  *)
    echo ""
    echo "Using ${SUDO} ${CK_PYTHON_PIP_BIN_FULL} ..."
    echo ""

    ${SUDO} ${CK_PYTHON_PIP_BIN_FULL} install --upgrade pip
    ${SUDO} ${CK_PYTHON_PIP_BIN_FULL} install requests matplotlib jupyter opencv-python

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

######################################################################################
echo ""
echo "Downloading and installing MXNet prebuilt binaries ..."
echo ""

# Check if has --system option
${CK_PYTHON_PIP_BIN_FULL} install --help > tmp-pip-help.tmp
if grep -q "\-\-system" tmp-pip-help.tmp ; then
 SYS=" --system"
fi
rm -f tmp-pip-help.tmp

${CK_PYTHON_PIP_BIN_FULL} install mxnet${MXNET_EXTRA}==${MXNET_PACKAGE_VER} -t ${INSTALL_DIR}/lib ${SYS}
if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

exit 0
