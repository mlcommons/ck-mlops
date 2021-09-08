#! /bin/bash

CUR_DIR=$PWD

export CK_ENV_MLPERF_INFERENCE_BERT=$CK_ENV_MLPERF_INFERENCE/language/bert

cd $CK_ENV_MLPERF_INFERENCE_BERT

# Adding path to tokenization
export PYTHONPATH="$CK_ENV_MLPERF_INFERENCE_BERT/DeepLearningExamples/TensorFlow/LanguageModeling/BERT:${PYTHONPATH}"

export BUILD_DIR=build

export DATA_DIR=$BUILD_DIR/data
export BERT_DIR=$DATA_DIR/bert_tf_v1_1_large_fp32_384_v2
export RESULT_DIR=$BUILD_DIR/result
export LOG_DIR=$BUILD_DIR/logs

mkdir -p $BUILD_DIR
mkdir -p $DATA_DIR
mkdir -p $BERT_DIR
mkdir -p $RESULT_DIR
mkdir -p $LOG_DIR

rm -f $LOG_DIR/*
rm -f $RESULT_DIR/*

ln -sf $CK_ENV_DATASET_SQUAD_DEV/dev-v1.1.json $DATA_DIR/dev-v1.1.json
ln -sf ${ML_MODEL_FILEPATH} $BERT_DIR/${ML_MODEL_FILENAME}

echo ""
echo "CK CMD: $CK_ENV_COMPILER_PYTHON_FILE run.py " \
     "--backend=$MLPERF_BACKEND " \
     "--mlperf_conf=$CK_ENV_MLPERF_INFERENCE_MLPERF_CONF " \
     "--scenario=$CK_LOADGEN_SCENARIO " \
     "$CK_LOADGEN_ASSEMBLED_OPTS" \
     "$EXTRA_OPS"

echo ""

# TODO: user.conf, --quantized & quantized model, --profile

$CK_ENV_COMPILER_PYTHON_FILE run.py \
     --backend=$MLPERF_BACKEND \
     --scenario=$CK_LOADGEN_SCENARIO \
     --mlperf_conf=$CK_ENV_MLPERF_INFERENCE_MLPERF_CONF \
     $CK_LOADGEN_ASSEMBLED_OPTS \
     $EXTRA_OPS

# Copying files from logs to tmp
cp -f $LOG_DIR/* $CUR_DIR
cp -f $RESULT_DIR/* $CUR_DIR

cd ${CUR_DIR}
