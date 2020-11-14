#! /bin/bash

#
# Copyright (c) 2020 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# See CK LICENSE.txt for licensing details.
#   
# Installation script for the EdgeTPU library.
#
function exit_if_error() {
  message=${1:-"unknown"}
  if [ "${?}" != "0" ]; then
    echo "Error: ${message}!"
    exit 1
  fi
}
wget --no-cookies ${PACKAGE_URL}${PACKAGE_NAME}
exit_if_error "wget failed"
dpkg -x $PACKAGE_NAME .
exit_if_error "dpkg failed"
cp -r usr/lib/*/libedgetpu* usr/lib/

cd ${INSTALL_DIR}/usr/lib/aarch64-linux-gnu/
ln -s libedgetpu.so.1.0 libedgetpu.so

return 0
