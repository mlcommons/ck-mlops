#!/bin/bash

echo "Logging into '${CK_DNNC_OUTPUT_DIR}/${CK_DNNC_LOG_FILE}'..."

# Create output dir.
mkdir -p ${CK_DNNC_OUTPUT_DIR}

# Copy the most recent DECENT log.
cp ${CK_DECENT_OUTPUT_DIR}/${CK_DECENT_LOG_FILE} ${CK_DNNC_OUTPUT_DIR}/${CK_DNNC_LOG_FILE}

LOG_ENTRY=`grep "MODEL_NAME" ${CK_DNNC_OUTPUT_DIR}/${CK_DNNC_LOG_FILE}`
CK_NET_NAME=`cut -d "=" -f2 <<< ${LOG_ENTRY}`

# Run the DNNC compiler.
echo >> ${CK_DNNC_OUTPUT_DIR}/${CK_DNNC_LOG_FILE}
echo "${CK_ENV_LIB_DNNDK_DNNC} \
--prototxt=${CK_DECENT_OUTPUT_DIR}/deploy.prototxt \
--caffemodel=${CK_DECENT_OUTPUT_DIR}/deploy.caffemodel \
--output_dir=${CK_DNNC_OUTPUT_DIR} \
--net_name=${CK_NET_NAME} \
--cpu_arch=${CK_CPU_ARCH} \
--dpu=${CK_DPU_TYPE} \
${CK_EXTRA_OPT}" \
>> ${CK_DNNC_OUTPUT_DIR}/${CK_DNNC_LOG_FILE}
${CK_ENV_LIB_DNNDK_DNNC} \
  --prototxt=${CK_DECENT_OUTPUT_DIR}/deploy.prototxt \
  --caffemodel=${CK_DECENT_OUTPUT_DIR}/deploy.caffemodel \
  --output_dir=${CK_DNNC_OUTPUT_DIR} \
  --net_name=${CK_NET_NAME} \
  --cpu_arch=${CK_CPU_ARCH} \
  --dpu=${CK_DPU_TYPE} \
  ${CK_EXTRA_OPT} \
  >> ${CK_DNNC_OUTPUT_DIR}/${CK_DNNC_LOG_FILE} \
  2>&1
