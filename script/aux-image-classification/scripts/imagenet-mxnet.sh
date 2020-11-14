. ${CK_AUX_TBD_SCRIPT}/scripts/common.sh $1 $2

export PYTHONPATH=${CK_AUX_TBD_SCRIPT}/sources-mxnet/source:${CK_AUX_TBD_SCRIPT}/sources-mxnet/source/common:$PWD/../source:$PYTHONPATH

DATASET_DIR=${CK_ENV_DATASET_IMAGENET_TRAIN_MXNET}

if [ "${MAX_NUMBER_OF_STEPS}" != "" ]
then
   export SUFFIX="--max_number_of_steps=${MAX_NUMBER_OF_STEPS} ${SUFFIX}"
fi

$PREFIX "${CK_ENV_COMPILER_PYTHON_FILE}" ../source/train_imagenet.py \
   --gpus ${GPU_NUM} --batch-size ${BATCH_SIZE} --image-shape ${IMAGE_SHAPE} --num-epochs ${NUM_EPOCHS_PER_DECAY} --network $1 \
   --data-train $DATASET_DIR $SUFFIX
