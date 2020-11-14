#! /bin/bash

#
# Download script for DeePhi calibration images.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developers: Flavio Vella, Anton Lokhmotov.
#

# ORIGINAL_PACKAGE_DIR (path to original package even if scripts are used from some other package or script)
# PACKAGE_DIR (path where scripts are reused)
# INSTALL_DIR

export IMAGE_PATH=${INSTALL_DIR}/${IMAGE_FILE}

#####################################################################
echo ""
echo "Checking whether '${IMAGE_PATH}' already exists ..."
if [ -f "${IMAGE_PATH}" ]
then
  echo "Warning: '${IMAGE_PATH}' already exists, skipping ..."
  exit 0
fi

#####################################################################
echo ""
echo "Downloading data from '${IMAGE_URL}' ..."
wget -c ${IMAGE_URL} -O ${IMAGE_PATH} --no-check-certificate
if [ "${?}" != "0" ] ; then
  echo "Error: Downloading archive from '${IMAGE_URL}' failed!"
  exit 1
fi

#####################################################################
echo ""
echo "Calculating the hash of '${IMAGE_PATH}' ..."
IMAGE_HASH_CALC=($(${IMAGE_HASH_CALCULATOR} ${IMAGE_PATH}))
if [ "${?}" != "0" ] ; then
  echo "Warning: Calculating the hash of '${IMAGE_PATH}' failed!"
fi
echo "Validating the hash of '${IMAGE_PATH}' ..."
if [ "${IMAGE_HASH_CALC}" != "${IMAGE_HASH_REF}" ] ; then
  echo "Warning: ${IMAGE_HASH_CALC} (calculated) not equal ${IMAGE_HASH_REF} (reference)"
fi

#####################################################################
echo ""
echo "Extracting images ..."
tar zxf $IMAGE_PATH resnet50/data -C $INSTALL_DIR/
mv $INSTALL_DIR/resnet50/data $INSTALL_DIR
rm -rf $INSTALL_DIR/resnet50/
rm ${IMAGE_PATH}

#####################################################################
exit 0
