#!/bin/bash

pushd $INSTALL_DIR

# Normalize names to dlrm_s_pytorch.onnx for CK to detect full path
# This is needed since the ONNX model filename is not the same as
# the .tar archive name

if [ -f dlrm_s_pytorch_10GB.onnx ]; then
    ln -sf dlrm_s_pytorch_10GB.onnx dlrm_s_pytorch.onnx
fi

if [ -f dlrm_s_pytorch_0505.onnx ]; then
    ln -sf dlrm_s_pytorch_0505.onnx dlrm_s_pytorch.onnx
fi

popd
