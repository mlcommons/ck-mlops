#! /bin/bash

# CK installation script for PyTorch package
#
# Developer(s):
#  * Grigori Fursin, dividiti/cTuning foundation
#

# PACKAGE_DIR
# INSTALL_DIR
# TF_PYTHON_URL


    # This is where pip will install the modules.
    # It has its own funny structure we don't control :
    #
EXTRA_PYTHON_SITE=${INSTALL_DIR}/python_deps_site

SHORT_PYTHON_VERSION=`${CK_ENV_COMPILER_PYTHON_FILE} -c 'import sys;print(sys.version[:3])'`
export PACKAGE_LIB_DIR="${EXTRA_PYTHON_SITE}/lib/python${SHORT_PYTHON_VERSION}/site-packages"
export PYTHONPATH=$PACKAGE_LIB_DIR:$PYTHONPATH

######################################################################################
echo ""
echo "Removing '${EXTRA_PYTHON_SITE}' ..."
rm -rf ${EXTRA_PYTHON_SITE}

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

${CK_ENV_COMPILER_PYTHON_FILE} -m pip install --ignore-installed numpy pyyaml mkl mkl-include setuptools cmake cffi typing --prefix=${EXTRA_PYTHON_SITE}  ${SYS}
if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

######################################################################################
MAJOR_PYTHON_VERSION=`${CK_ENV_COMPILER_PYTHON_FILE} -c 'import sys;print(sys.version[0])'`

######################################################################################
echo ""
echo "Cloning ..."
echo ""

cd ${INSTALL_DIR}
git clone --recursive ${PACKAGE_URL}

cd pytorch

export NO_CUDA=${NO_CUDA}

######################################################################################
echo ""
echo "Building ..."
echo ""

${CK_ENV_COMPILER_PYTHON_FILE} setup.py install --prefix=${EXTRA_PYTHON_SITE}
if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

######################################################################################
echo "Preparing symbolic link for lib ..."
echo ""

ln -s $PACKAGE_LIB_DIR ${INSTALL_DIR}/lib

exit 0
