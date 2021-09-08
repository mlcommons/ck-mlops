#! /bin/bash

echo "*********************************************************"

if [ "x${CK_MLPERF_AUDIT_SCRIPT}" != "x" ] ; then
  echo ""
  echo "${CK_ENV_COMPILER_PYTHON_FILE} ${CK_MLPERF_AUDIT_SCRIPT} ${CK_MLPERF_COMPLIANCE_EXTRA} -o ${CK_MLPERF_COMPLIANCE_DIR}"
  echo ""

  ${CK_ENV_COMPILER_PYTHON_FILE} ${CK_MLPERF_AUDIT_SCRIPT} ${CK_MLPERF_COMPLIANCE_EXTRA} -o ${CK_MLPERF_COMPLIANCE_DIR} > compliance.txt 2>&1
fi
