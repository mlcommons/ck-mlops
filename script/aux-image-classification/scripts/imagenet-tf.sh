. ${CK_AUX_TBD_SCRIPT}/scripts/common.sh $1 $2

export PYTHONPATH=${CK_AUX_TBD_SCRIPT}/sources-tf/source:$PWD/../source:$PYTHONPATH

DATASET_DIR=${CK_ENV_DATASET_IMAGENET_TRAIN_TF} # path to your TFRecords folder

if [ "${MAX_NUMBER_OF_STEPS}" != "" ]
then
   export SUFFIX="--max_number_of_steps=${MAX_NUMBER_OF_STEPS} ${SUFFIX}"
fi

$PREFIX "${CK_ENV_COMPILER_PYTHON_FILE}" ${CK_AUX_TBD_SCRIPT}/sources-tf/source/train_image_classifier.py --train_dir=$TRAIN_DIR --dataset_dir=$DATASET_DIR \
	--model_name=$1 --optimizer=${LEARNING_OPTIMIZER} --batch_size=${BATCH_SIZE} \
	--learning_rate=${LEARNING_RATE} --learning_rate_decay_factor=${LEARNING_RATE_DECAY_FACTOR} --num_epochs_per_decay=${NUM_EPOCHS_PER_DECAY} \
	--weight_decay=${WEIGHT_DECAY} $SUFFIX

