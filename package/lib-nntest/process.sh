#! /bin/bash

#
# Copyright (c) 2015-2017 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Installation script for CK packages.
#
# Developer(s): Grigori Fursin, 2015
#

# PACKAGE_DIR
# INSTALL_DIR

echo ""
echo "Copying NNTest to src dir ..."
echo ""

mkdir -p ${INSTALL_DIR}/install/include

cp ${PACKAGE_DIR}/*.h ${INSTALL_DIR}/install/include
cp ${PACKAGE_DIR}/README* ${INSTALL_DIR}
