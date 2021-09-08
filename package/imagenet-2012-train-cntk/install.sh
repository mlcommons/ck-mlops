#! /bin/bash

#
# Installation script for the 2012 ImageNet Large Scale Visual Recognition
# Preparing (ILSVRC'12) train dataset for CNTK
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

"${CK_ENV_COMPILER_PYTHON_FILE}" "${PACKAGE_DIR}/dataset/create_train_map.py" $DATA_DIR
if [ "${?}" != "0" ] ; then
  echo "Error: error processing ImageNet for CNTK!"
  exit 1
fi

export CK_GROUND_TRUTH="${PACKAGE_DIR}/dataset/ILSVRC2012_validation_ground_truth.txt"
export CK_VAL_MAP=${INSTALL_DIR}/install/val_map.txt

"${CK_ENV_COMPILER_PYTHON_FILE}" "${PACKAGE_DIR}/dataset/create_val_map.py"
if [ "${?}" != "0" ] ; then
  echo "Error: error processing ImageNet for CNTK!"
  exit 1
fi

#####################################################################
echo ""
echo "Successfully processed ILSVRC'12 train dataset for CNTK ..."
exit 0
