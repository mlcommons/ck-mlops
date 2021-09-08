#! /bin/bash

MLPERF_BACKUP_DIR="${CK_ENV_MLPERF_INFERENCE_RESULTS}/../backup"

if [ "${CLEAN_MLPERF_BACKUP}" == "YES" ] ; then
 echo "Cleaning backup dir ${MLPERF_BACKUP_DIR}"
 rm -rf ${MLPERF_BACKUP_DIR}
 echo ""
fi

${CK_ENV_COMPILER_PYTHON_FILE} ${CK_ENV_MLPERF_INFERENCE}/tools/submission/truncate_accuracy_log.py \
   --input ${CK_ENV_MLPERF_INFERENCE_RESULTS} \
   --submitter ${CK_MLPERF_SUBMITTER} \
   --backup ${MLPERF_BACKUP_DIR}
