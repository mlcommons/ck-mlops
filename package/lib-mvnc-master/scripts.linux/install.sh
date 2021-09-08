#! /bin/bash

#
# Installation script for MVNC
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2017;
#

# PACKAGE_DIR
# INSTALL_DIR

echo "**************************************************************"
echo "Executing make install ..."

cd ${INSTALL_DIR}/${PACKAGE_SUB_DIR}

make install
if [ "${?}" != "0" ] ; then
  echo "Error: cmake failed!"
  exit 1
fi

return 0
