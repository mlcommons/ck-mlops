#!/bin/sh

# Call common script to set up CUDA profiling

. ${CK_AUX_TBD_SCRIPT}/scripts/common.sh dummy $2

# Check extra vars

if [ "$2" = "--profile" ] 
then
  EXTRA_CMD="${EXTRA_CMD} --train_steps=400"
elif [ "$2" = "--profile-fp32" ]
then
  EXTRA_CMD="${EXTRA_CMD} --train_steps=400"
fi

# Run code

HPARAMS="batch_size=${BATCH_SIZE}"

$PREFIX "${CK_ENV_COMPILER_PYTHON_FILE}" ../source/tensor2tensor/tensor2tensor/bin/t2t-trainer.py \
    --data_dir=${CK_ENV_DATASET_WMT32K_ENGLISH_GERMAN_TF} \
    --problems=${CK_ENV_DATASET_WMT32K_ENGLISH_GERMAN_TF_PROBLEMS} \
    --model=$1 \
    --hparams_set=$1_base_single_gpu \
    --output_dir=t2t_train/base \
    --hparams="${HPARAMS}" ${EXTRA_CMD}
