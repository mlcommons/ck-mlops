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


function exit_if_error() {
  message=${1:-"unknown"}
  if [ "${?}" != "0" ]; then
    echo "Error: ${message}!"
    exit 1
  fi
}

echo ""
echo "Installing GLOW LSTM RNNT Pre plugin ..."
echo ""

PLUGIN_DIR=${INSTALL_DIR}/plugin/
BUNDLE_DIR=${INSTALL_DIR}/bundle/

mkdir -p ${PLUGIN_DIR}
mkdir -p ${BUNDLE_DIR}

cp -r ${PACKAGE_DIR}/${PLUGIN_NAME} ${PLUGIN_DIR}
ESCAPED_PLUGIN_DIR=$(echo ${PLUGIN_DIR} | sed 's_/_\\/_g')
sed -i -e "s/PLUGIN_DIR/$ESCAPED_PLUGIN_DIR/g" ${PLUGIN_DIR}/${PLUGIN_NAME}
sed -i -e "s/EMBEDDING_WIDTH/${PLUGIN_LSTM_INPUT_SIZE}/g" ${PLUGIN_DIR}/${PLUGIN_NAME}
sed -i -e "s/HIDDEN_WIDTH/${PLUGIN_LSTM_HIDDEN_SIZE}/g" ${PLUGIN_DIR}/${PLUGIN_NAME}
sed -i -e "s/NUM_LAYERS/${PLUGIN_LSTM_NUM_LAYERS}/g" ${PLUGIN_DIR}/${PLUGIN_NAME}

echo "Converting ONNX to Glow bundle ..."
echo ""


${CK_ENV_COMPILER_GLOW}/bin/model-compiler -backend=CPU -model=${CK_NNTEST_PLUGIN_PRE_ONNX}/plugin/model.onnx -emit-bundle=${BUNDLE_DIR} -relocation-model=pic -bundle-api-verbose -onnx-define-symbol=batch,1
exit_if_error "Conversion from ONNX to Glow failed"


echo "Building Glow bundle to plugin (may take some time) ..."
echo ""

${CK_CXX_FULL_PATH} -shared -fPIC -O3 \
                    -I${BUNDLE_DIR} \
                    -D_EMBEDDING_WIDTH=${PLUGIN_LSTM_INPUT_SIZE} \
                    -D_HIDDEN_WIDTH=${PLUGIN_LSTM_HIDDEN_SIZE} \
                    -D_NUM_LAYERS=${PLUGIN_LSTM_NUM_LAYERS} \
                     ${ORIGINAL_PACKAGE_DIR}/wrapper.cpp \
                     ${BUNDLE_DIR}/model.o \
                     -o ${PLUGIN_DIR}/model.so
exit_if_error "Building Glow plugin failed"


