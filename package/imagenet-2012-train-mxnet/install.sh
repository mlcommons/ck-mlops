#! /bin/bash

#
# Installation script for the 2012 ImageNet Large Scale Visual Recognition
# Preparing (ILSVRC'12) train dataset for MXNet
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, Grigori.Fursin@cTuning.org, 2018

# PACKAGE_DIR
# INSTALL_DIR

cd ${INSTALL_DIR}
mkdir install
cd install

DATA_DIR="${CK_ENV_DATASET_IMAGENET_TRAIN}"

"${CK_ENV_COMPILER_PYTHON_FILE}" "${PACKAGE_DIR}/dataset/im2rec.py" --list True --recursive True imagenet1k $DATA_DIR
if [ "${?}" != "0" ] ; then
  echo "Error: error processing ImageNet for MXNet!"
  exit 1
fi

"${CK_ENV_COMPILER_PYTHON_FILE}" "${PACKAGE_DIR}/dataset/im2rec.py" --resize 480 --quality 95 --num-thread 16 imagenet1k $DATA_DIR
if [ "${?}" != "0" ] ; then
  echo "Error: error processing ImageNet for MXNet!"
  exit 1
fi

#####################################################################
echo ""
echo "Successfully processed ILSVRC'12 train dataset for MXNet ..."
exit 0
