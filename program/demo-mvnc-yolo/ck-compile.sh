#!/bin/sh

# Collective Knowledge (program)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org

echo "Compiling YOLO model to NCS graph file ..."

mvNCCompile ${CK_ENV_MODEL_CAFFE}/yolo_tiny_deploy.prototxt -w ${CK_ENV_MODEL_CAFFE_WEIGHTS} -s ${PARAM_S}

return ${?}

