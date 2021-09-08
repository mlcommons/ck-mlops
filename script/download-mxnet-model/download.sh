#! /bin/bash

#
# Download script for Caffe model weights.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Anton Lokhmotov, anton@dividiti.com, 2016
# - Grigori Fursin, grigori@dividiti.com, 2016

# ORIGINAL_PACKAGE_DIR (path to original package even if scripts are used from some other package or script)
# PACKAGE_DIR (path where scripts are reused)
# INSTALL_DIR

X1=${MXNET_URL_MODEL_PARAMS}/${MXNET_MODEL_PARAMS}
if [ "${MXNET_MODEL_PARAMS}" != "" ] ; then
  wget -c ${X1} -O ${MXNET_MODEL_PARAMS} --no-check-certificate

  if [ "${?}" != "0" ] ; then
    echo "Error: download failed!"
    exit 1
  fi
fi

X2=${MXNET_URL_MODEL_JSON}/${MXNET_MODEL_JSON}
if [ "${MXNET_MODEL_JSON}" != "" ] ; then
  wget -c ${X2} -O ${MXNET_MODEL_JSON} --no-check-certificate

  if [ "${?}" != "0" ] ; then
    echo "Error: download failed!"
    exit 1
  fi
fi

X3=${MXNET_URL_MODEL_LABELS}/${MXNET_MODEL_LABELS}
if [ "${MXNET_MODEL_LABELS}" != "" ] ; then
  wget -c ${X3} -O ${MXNET_MODEL_LABELS} --no-check-certificate

  if [ "${?}" != "0" ] ; then
    echo "Error: download failed!"
    exit 1
  fi
fi

exit 0
