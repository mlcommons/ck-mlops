#! /bin/bash

# CK installation script for CNTK package
#
# Developer(s):
#  * Grigori Fursin, dividiti/cTuning foundation
#

# PACKAGE_DIR
# INSTALL_DIR

export CNTK_LIB_DIR=${INSTALL_DIR}/lib

echo ""
echo "Removing '${CNTK_LIB_DIR}' ..."
rm -rf ${CNTK_LIB_DIR}

######################################################################################
# Print info about possible issues
echo ""
echo "Note that you sometimes need to upgrade your pip to the latest version"
echo "to avoid well-known issues with user/system space installation..."

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
# Misc vars
EXTRA_PYTHON_SITE=${INSTALL_DIR}/python_deps_site
SHORT_PYTHON_VERSION=`${CK_ENV_COMPILER_PYTHON_FILE} -c 'import sys;print(sys.version[:3])'`
export PACKAGE_LIB_DIR="${EXTRA_PYTHON_SITE}/lib/python${SHORT_PYTHON_VERSION}/site-packages"

rm -rf ${EXTRA_PYTHON_SITE}

######################################################################################
echo "Downloading and installing Python deps ..."
echo ""

${CK_ENV_COMPILER_PYTHON_FILE} -m pip install requests matplotlib jupyter opencv-python --ignore-installed --prefix=${EXTRA_PYTHON_SITE}  ${SYS}
if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

######################################################################################
URL=https://cntk.ai/PythonWheel/${CNTK_PACKAGE_TYPE}/cntk${CNTK_PACKAGE_EXT}-${CNTK_PACKAGE_VER}-${CNTK_PACKAGE_FILE_EXT}

echo ""
echo "Downloading and installing CNTK prebuilt binaries (${URL}) ..."
echo ""

${CK_ENV_COMPILER_PYTHON_FILE} -m pip install ${URL} --ignore-installed --prefix=${EXTRA_PYTHON_SITE} ${SYS}
if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

######################################################################################
# Making compatible with CK
ln -s $PACKAGE_LIB_DIR ${INSTALL_DIR}/lib

######################################################################################
URL2=https://cntk.ai/BinaryDrop/${CNTK_PACKAGE_BINARY_ARC}

echo ""
echo "Downloading and installing CNTK prebuilt binaries (${URL2}) ..."
echo ""

cd $INSTALL_DIR/

wget ${URL2}
if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

echo ""
echo "Ungzipping ${CNTK_PACKAGE_BINARY_ARC} ..."
echo ""
gzip -d ${CNTK_PACKAGE_BINARY_ARC}

echo ""
echo "Untarring ${CNTK_PACKAGE_BINARY_ARC2} ..."
echo ""
tar xvf ${CNTK_PACKAGE_BINARY_ARC2}

rm ${CNTK_PACKAGE_BINARY_ARC2}

exit 0
