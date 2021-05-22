#! /bin/bash

#
# Copyright (c) 2020 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Installation script for CK packages.
#
# Developer(s): Gavin Simpson
#

# PACKAGE_DIR
# INSTALL_DIR

echo ""
echo "Installing PyTorch LSTM RNNT Pre plugin ..."
echo ""

PLUGIN_DIR=${INSTALL_DIR}/plugin/

mkdir -p ${PLUGIN_DIR}

cp -r ${PACKAGE_DIR}/${PLUGIN_SUBDIR}/* ${PLUGIN_DIR}

ESCAPED_CHECKPOINT_DIR=$(echo ${CK_ENV_MODEL_PYTORCH} | sed 's_/_\\/_g')
sed -i -e "s/RNNT_CHECKPOINT/$ESCAPED_CHECKPOINT_DIR/g" ${PLUGIN_DIR}/${PLUGIN_NAME}

