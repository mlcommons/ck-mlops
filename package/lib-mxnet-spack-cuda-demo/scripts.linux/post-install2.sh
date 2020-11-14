#! /bin/bash

#
# Installation script for MXNet via spack
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer(s):
# - Grigori Fursin, 2018
#

# PACKAGE_DIR
# INSTALL_DIR

# Add path to Spack
export PATH=$INSTALL_DIR/src/bin:$PATH

# Prepare config.yaml
echo ""
echo "Preparing config.yaml ..."
mkdir -p $INSTALL_DIR/src/etc/spack

echo "config:" > $INSTALL_DIR/src/etc/spack/config.yaml
echo "  install_tree: $INSTALL_DIR/spack" >> $INSTALL_DIR/src/etc/spack/config.yaml
echo "" >> $INSTALL_DIR/src/etc/spack/config.yaml
echo "  install_path_scheme: '\${PACKAGE}'" >> $INSTALL_DIR/src/etc/spack/config.yaml
echo "" >> $INSTALL_DIR/src/etc/spack/config.yaml
echo "  build_jobs: ${CK_HOST_CPU_NUMBER_OF_PROCESSORS}" >> $INSTALL_DIR/src/etc/spack/config.yaml

# Prepare packages.yaml for OpenGL

# First assembling lib/include into one directory
mkdir $INSTALL_DIR/opengl
ln -s $CK_ENV_LIB_OPENGL_LIB $INSTALL_DIR/opengl/lib
ln -s $CK_ENV_LIB_OPENGL_INCLUDE $INSTALL_DIR/opengl/include

echo "packages:" > $INSTALL_DIR/src/etc/spack/packages.yaml
echo "  opengl:" >> $INSTALL_DIR/src/etc/spack/packages.yaml
echo "    paths:" >> $INSTALL_DIR/src/etc/spack/packages.yaml
echo "      opengl@4.5.0: $INSTALL_DIR/opengl" >> $INSTALL_DIR/src/etc/spack/packages.yaml
echo "    buildable: False" >> $INSTALL_DIR/src/etc/spack/packages.yaml

echo ""
echo "Invoking \"spack install mxnet ^libjpeg ^protobuf@3.1.0 ^vtk+osmesa\""

spack clean --misc-cache

spack install mxnet ^libjpeg ^protobuf@3.1.0 ^opengl
# ^llvm@5.0.1 ^python@3.5.1 ^opencv@3.1.0 ^protobuf@3.1.0 ^opengl
# ^vtk+osmesa

if [ "${?}" != "0" ] ; then
  echo "Error: cmake failed!"
  exit 1
fi

return 0
