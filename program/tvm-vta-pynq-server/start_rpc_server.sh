#!/bin/bash

echo "********************************************************************************"
echo "Local IP:"
echo ""

ifconfig eth0
echo "********************************************************************************"

#cd ${CK_ENV_LIB_TVM_SRC}

PROJROOT=${CK_ENV_LIB_TVM_SRC}
export PYTHONPATH=${PYTHONPATH}:${PROJROOT}/python:${PROJROOT}/vta/python

${CK_ENV_COMPILER_PYTHON_FILE} -m vta.exec.rpc_server
