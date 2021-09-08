#! /bin/bash

#
# Installation script for LLVM.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2015
#

# PACKAGE_DIR
# INSTALL_DIR

cd ${INSTALL_DIR}

${CK_ENV_COMPILER_PYTHON_FILE} ${PACKAGE_DIR}/model.py

rm -f ${MXNET_MODEL_LABELS}

wget ${MXNET_URL_MODEL_LABELS}/${MXNET_MODEL_LABELS}

exit 0
