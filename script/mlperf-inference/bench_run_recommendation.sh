#! /bin/bash

CUR_DIR=$PWD

cd ${CK_ENV_MLPERF_INFERENCE}/recommendation/dlrm/pytorch

echo ""
echo "${CK_MLPERF_CMD_PREFIX} ${CK_ENV_COMPILER_PYTHON_FILE} python/main.py "\
     "--profile ${MLPERF_PROFILE}-${MLPERF_PROFILE_BACKEND}${MLPERF_PROFILE_EXT} "\
     "--mlperf_conf=$CK_ENV_MLPERF_INFERENCE_MLPERF_CONF " \
     "--scenario ${CK_LOADGEN_SCENARIO} "\
     "--dataset-path ${DATA_DIR} "\
     "$CK_LOADGEN_ASSEMBLED_OPTS" \
     "$EXTRA_OPS"

echo ""
${CK_MLPERF_CMD_PREFIX} ${CK_ENV_COMPILER_PYTHON_FILE} python/main.py \
    --profile ${MLPERF_PROFILE}-${MLPERF_PROFILE_BACKEND}${MLPERF_PROFILE_EXT} \
    --mlperf_conf=$CK_ENV_MLPERF_INFERENCE_MLPERF_CONF \
    --scenario ${CK_LOADGEN_SCENARIO} \
    --dataset-path ${DATA_DIR} \
    $CK_LOADGEN_ASSEMBLED_OPTS \
    $EXTRA_OPS

cd ${CUR_DIR}
