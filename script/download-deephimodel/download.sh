#! /bin/bash

#
# Download script for Caffe/DeePhi model.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developers: Grigori Fursin, Flavio Vella, Anton Lokhmotov.
#

# ORIGINAL_PACKAGE_DIR (path to original package even if scripts are used from some other package or script)
# PACKAGE_DIR (path where scripts are reused)
# INSTALL_DIR

export MODEL_PATH=${INSTALL_DIR}/${MODEL_FILE}

#####################################################################
#echo ""
#echo "Copying net topology files to '${INSTALL_DIR}' ..."
#cp -f ${ORIGINAL_PACKAGE_DIR}/* ${INSTALL_DIR}
#if [ "${?}" != "0" ] ; then
#  echo "Error: copying net topology files failed!"
#  exit 1
#fi

#####################################################################
echo ""
echo "Checking whether '${MODEL_PATH}' already exists ..."
if [ -f "${MODEL_PATH}" ]
then
  echo "Warning: '${MODEL_PATH}' already exists, skipping ..."
  exit 0
fi

#####################################################################
echo ""
echo "Downloading the weights from '${MODEL_URL}' ..."
wget -c ${MODEL_URL} -O ${MODEL_PATH} --no-check-certificate
if [ "${?}" != "0" ] ; then
  echo "Error: Downloading archive from '${MODEL_URL}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Calculating the hash of '${MODEL_PATH}' ..."
MODEL_HASH_CALC=($(${MODEL_HASH_CALCULATOR} ${MODEL_PATH}))
if [ "${?}" != "0" ] ; then
  echo "Warning: Calculating the hash of '${MODEL_PATH}' failed!"
fi
echo "Validating the hash of '${MODEL_PATH}' ..."
if [ "${MODEL_HASH_CALC}" != "${MODEL_HASH_REF}" ] ; then
  echo "Warning: ${MODEL_HASH_CALC} (calculated) not equal ${MODEL_HASH_REF} (reference)"
fi
#####################################################################
echo ""
echo "Extracting models"
tar zxf $MODEL_PATH --strip-components=1 -C $INSTALL_DIR/ 

#FIXME remove the archive optionally

#####################################################################

#####################################################################

echo ""
echo "Installed ${MODEL_ENV}=${MODEL_PATH}"
exit 0
