# DEPRECATED!

#! /bin/bash

COMMON_SCRIPTS=`ck find script:mlperf-inference`

. ${COMMON_SCRIPTS}/bench_start.sh

export DATA_DIR=${CK_ENV_DATASET_IMAGENET_VAL}

echo ""
echo "./run_local.sh $CK_MLPERF_BACKEND $CK_MLPERF_MODEL $CK_MLPERF_DEVICE --scenario $CK_LOADGEN_SCENARIO $CK_LOADGEN_ASSEMBLED_OPTS"
echo ""

pushd ${CK_ENV_MLPERF_INFERENCE_VISION}/classification_and_detection
./run_local.sh $CK_MLPERF_BACKEND $CK_MLPERF_MODEL $CK_MLPERF_DEVICE --scenario $CK_LOADGEN_SCENARIO $CK_LOADGEN_ASSEMBLED_OPTS 
popd

. ${COMMON_SCRIPTS}/bench_end.sh
