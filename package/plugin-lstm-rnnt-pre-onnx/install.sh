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
echo "Installing ONNX LSTM RNNT Pre plugin ..."
echo ""

PLUGIN_DIR=${INSTALL_DIR}/plugin/
mkdir -p ${PLUGIN_DIR}

${CK_PYTHON_BIN} ${ORIGINAL_PACKAGE_DIR}/convert_to_onnx.py --dest=${PLUGIN_DIR}/model.onnx --input_size=${PLUGIN_LSTM_INPUT_SIZE} --hidden_size=${PLUGIN_LSTM_HIDDEN_SIZE} --layers=${PLUGIN_LSTM_NUM_LAYERS}

cp -r ${PACKAGE_DIR}/${PLUGIN_SUBDIR}/${PLUGIN_NAME} ${PLUGIN_DIR}

ESCAPED_PLUGIN_DIR=$(echo ${PLUGIN_DIR} | sed 's_/_\\/_g')
sed -i -e "s/PLUGIN_DIR/$ESCAPED_PLUGIN_DIR/g" ${PLUGIN_DIR}/${PLUGIN_NAME}



