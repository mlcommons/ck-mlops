#! /bin/bash

#
# Installation script for the 2012 ImageNet Large Scale Visual Recognition
# Preparing (ILSVRC'12) train dataset for TensorFlow
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, Grigori.Fursin@cTuning.org, 2018

# PACKAGE_DIR
# INSTALL_DIR

cd ${PACKAGE_DIR}

. dataset/convert_imagenet.sh
if [ "${?}" != "0" ] ; then
  echo "Error: error processing ImageNet for TensorFlow!"
  exit 1
fi

#####################################################################
echo ""
echo "Successfully processed ILSVRC'12 train dataset for TensorFlow ..."
exit 0
