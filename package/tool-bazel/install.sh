#! /bin/bash

#
# Installation script for Bazel
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Grigori Fursin, https://fursin.net
#

# PACKAGE_DIR
# INSTALL_DIR

FULL_PACKAGE_URL=$PACKAGE_URL/$PACKAGE_NAME

################################################################################
echo "************************************************************"
echo "Downloading Bazel from '${FULL_PACKAGE_URL}' ..."
echo ""

wget ${FULL_PACKAGE_URL} -O ${PACKAGE_NAME} --no-check-certificate
if [ "${?}" != "0" ] ; then
  echo "Error: Downloading Bazel from '${FULL_PACKAGE_URL}' failed!"
  exit 1
fi

################################################################################
echo "************************************************************"
echo "Running Bazel installer ..."
echo ""

chmod 755 ./$PACKAGE_NAME
./$PACKAGE_NAME --prefix=$PWD/install
if [ "${?}" != "0" ] ; then
  echo "Error: Installing Bazel failed!"
  exit 1
fi

################################################################################
echo "************************************************************"
echo "Cleaning Bazel installer ..."
echo ""

rm -f ./$PACKAGE_NAME

###############################################################################
echo "************************************************************"
echo "Successfully installed Bazel into '${INSTALL_DIR}'."
echo ""

