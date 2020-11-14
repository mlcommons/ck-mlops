#! /bin/bash

#
# Installation script for Open Model Zoo.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer(s):
# - Gavin Simpson, 2020.
#


###############################################################################
echo ""
echo "Setting up Accuracy Checker."
echo ""

if [ "${PACKAGE_VERSION}" = "2019_R3.1" ] || [ "${PACKAGE_VERSION}" = "2019_R3" ]; then

read -d '' CMD <<END_OF_CMD
  cd ${INSTALL_DIR}/open_model_zoo-${PACKAGE_VERSION}/tools/accuracy_checker/ ; \
  ${CK_PYTHON_BIN} ./setup.py build ; \
  rm -f ${INSTALL_DIR}/lib ; \
  ln -s ${INSTALL_DIR}/open_model_zoo-${PACKAGE_VERSION}/tools/accuracy_checker/build/lib/ ${INSTALL_DIR}
END_OF_CMD

echo ${CMD}
eval ${CMD}

else
  #TBD
  echo "Accuracy Checker not yet supported for ${PACKAGE_VERSION}"
fi

if [ "${?}" != "0" ] ; then
  echo "Error: Setting up Accuracy Checker failed!"
  exit 1
fi

###############################################################################
echo ""
echo "Accuracy Checker successfully set up."
echo ""
