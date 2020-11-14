#!/bin/bash

if [ "${CK_CALIBRATE_IMAGENET}" != "yes" ]; then

  echo ""
  echo "######################################################################################"
  echo "Converting TensorFlow model to OpenVINO format..."
  echo ""

  if [ "${CK_ENV_TENSORFLOW_MODEL_MODEL_NAME}" = "MLPerf SSD-MobileNet" ] ; then
    CUSTOM="--tensorflow_object_detection_api_pipeline_config $(dirname ${CK_ENV_TENSORFLOW_MODEL_TF_FROZEN_FILEPATH})/pipeline.config \
        --tensorflow_use_custom_operations_config ${CK_ENV_LIB_OPENVINO_MO_DIR}/extensions/front/tf/ssd_v2_support.json"
  else
    CUSTOM=""
  fi

  if [ ${ML_MODEL_COLOUR_CHANNELS_BGR:-NO} == "YES" ] ; then
    REVERSE_INPUT_CHANNELS="--reverse_input_channels"
  else
    REVERSE_INPUT_CHANNELS=""
  fi

  read -d '' CMD <<END_OF_CMD
  ${CK_ENV_COMPILER_PYTHON_FILE} \
    ${CK_ENV_LIB_OPENVINO_MO_DIR}/mo.py \
    --model_name ${MODEL_NAME} \
    --input_model ${CK_ENV_TENSORFLOW_MODEL_TF_FROZEN_FILEPATH} \
    --input_shape [1,${CK_ENV_TENSORFLOW_MODEL_IMAGE_HEIGHT},${CK_ENV_TENSORFLOW_MODEL_IMAGE_WIDTH},3] \
    ${REVERSE_INPUT_CHANNELS} \
    ${CUSTOM}
END_OF_CMD

  echo ${CMD}
  eval ${CMD}

  if [ "${?}" != "0" ] ; then
    echo "Error: Conversion to OpenVINO format failed!"
    exit 1
  fi

else # END OF if [ "${CK_CALIBRATE_IMAGENET}" != "yes" ]

  echo ""
  echo "######################################################################################"
  echo "Converting annotations ..."
  echo ""

  read -d '' CMD <<END_OF_CMD
  ${CK_ENV_COMPILER_PYTHON_FILE} \
    ${CK_ENV_LIB_OPENVINO_CONVERT_ANNOTATION_PY} \
    imagenet \
    --annotation_file ${CK_DATASET_IMAGENET_CALIBRATION_VAL_MAP_PATH} \
    --labels_file ${CK_CAFFE_IMAGENET_SYNSET_WORDS_TXT} \
    --has_background ${CK_OPENVINO_ANNOTATION_CONVERSION_HAS_BACKGROUND} \
    --output_dir ${INSTALL_DIR}
END_OF_CMD

  echo ${CMD}
  eval ${CMD}

  if [ "${?}" != "0" ] ; then
    echo "Error: Converting annotations failed!"
    exit 1
  fi


  echo ""
  echo "######################################################################################"
  echo "Running calibration ..."
  echo ""

  read -d '' CMD <<END_OF_CMD
  LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${CK_ENV_LIB_OPENVINO_LIB_DIR} ; \
  ${CK_ENV_COMPILER_PYTHON_FILE} \
    ${CK_ENV_LIB_OPENVINO_CALIBRATE_PY} \
    -c ${INSTALL_DIR}/config.yml \
    -M ${CK_ENV_LIB_OPENVINO_MO_DIR} \
    -e ${CK_ENV_LIB_OPENVINO_LIB_DIR} \
    -C ${INSTALL_DIR} \
    --output_dir ${INSTALL_DIR}
END_OF_CMD

  echo ${CMD}
  eval ${CMD}

  if [ "${?}" != "0" ] ; then
    echo "Error: Calibration failed!"
    exit 1
  fi


  echo ""
  echo "######################################################################################"
  echo "Renaming '${MODEL_NAME_I8}.{bin,xml}' to '${MODEL_NAME}.{bin,xml}' ..."
  echo ""

  mv ${MODEL_NAME_I8}.bin ${MODEL_NAME}.bin
  mv ${MODEL_NAME_I8}.xml ${MODEL_NAME}.xml

  if [ "${?}" != "0" ] ; then
    echo "Error: Renaming failed!"
    exit 1
  fi

fi # END OF if/else [ "${CK_CALIBRATE_IMAGENET}" != "yes" ]

echo "Done."
exit 0
