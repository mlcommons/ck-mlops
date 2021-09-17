#! /bin/bash

CUR_DIR=$PWD

export CK_ENV_MLPERF_INFERENCE_MEDICAL_IMAGING=$CK_ENV_MLPERF_INFERENCE/vision/medical_imaging/3d-unet-brats19

# historical 3d-unet directory name
if [ ! -d $CK_ENV_MLPERF_INFERENCE_MEDICAL_IMAGING ]; then
    export CK_ENV_MLPERF_INFERENCE_MEDICAL_IMAGING=$CK_ENV_MLPERF_INFERENCE/vision/medical_imaging/3d-unet
fi

cd $CK_ENV_MLPERF_INFERENCE_MEDICAL_IMAGING

# Adding path to nnUnet library
export PYTHONPATH="$CK_ENV_MLPERF_INFERENCE_MEDICAL_IMAGING/nnUnet:${PYTHONPATH}"

export BUILD_DIR=build

export DOWNLOADED_DATA_DIR=$BUILD_DIR/MICCAI_BraTS_2019_Data_Training
export RAW_DATA_DIR=$BUILD_DIR/raw_data
export PREPROCESSED_DATA_DIR=$BUILD_DIR/preprocessed_data
export POSTPROCESSED_DATA_DIR=$BUILD_DIR/postprocessed_data
export RESULT_DIR=$BUILD_DIR/result
export LOG_DIR=$BUILD_DIR/logs
# PLANS_PKL_PATH set in loadgen_preprocess
# export PLANS_PKL_PATH=$ML_MODEL_ROOT/nnUNet/3d_fullres/Task043_BraTS2019/nnUNetTrainerV2__nnUNetPlansv2.mlperf.1

# Env variables needed by nnUnet
export nnUNet_raw_data_base=$RAW_DATA_DIR
export nnUNet_preprocessed=$PREPROCESSED_DATA_DIR
export RESULTS_FOLDER=$RESULT_DIR

mkdir -p $BUILD_DIR
mkdir -p $POSTPROCESSED_DATA_DIR

echo
echo "Preprocessing data (this may take a while) ..."
echo

# Preprocessing downloaded data -> raw data (build/raw_data)
$CK_ENV_COMPILER_PYTHON_FILE Task043_BraTS_2019.py \
    --downloaded_data_dir=$CK_ENV_DATASET_BRATS_2019_TRAIN

# Preprocessing raw data -> preprocessed data (build/preprocessed_data)
$CK_ENV_COMPILER_PYTHON_FILE preprocess.py \
    --model_dir=$PLANS_PKL_PATH

echo ""
echo "CK CMD: $CK_ENV_COMPILER_PYTHON_FILE run.py " \
     "--backend=$MLPERF_BACKEND " \
     "--scenario=$CK_LOADGEN_SCENARIO " \
     "--mlperf_conf=$CK_ENV_MLPERF_INFERENCE_MLPERF_CONF " \
     "--model=$ML_MODEL_FILEPATH" \
     "--model_dir=$PLANS_PKL_PATH" \
     "$CK_LOADGEN_ASSEMBLED_OPTS" \
     "$EXTRA_OPS"

echo ""

# TODO: user.conf

$CK_ENV_COMPILER_PYTHON_FILE run.py \
     --backend=$MLPERF_BACKEND \
     --scenario=$CK_LOADGEN_SCENARIO \
     --mlperf_conf=$CK_ENV_MLPERF_INFERENCE_MLPERF_CONF \
     --model=$ML_MODEL_FILEPATH \
     --model_dir=$PLANS_PKL_PATH \
     $CK_LOADGEN_ASSEMBLED_OPTS \
     $EXTRA_OPS

# Copying files from logs to tmp
cp -f $LOG_DIR/* $CUR_DIR

cd ${CUR_DIR}
