#!/bin/bash

# NB: To execute commands remotely, place the following lines into /root/.bash_profile:
# # Collective Knowledge.
# export CK_ROOT=/root/CK
# export PATH=$CK_ROOT/bin:$PATH
# export CK_TOOLS=$HOME/CK_TOOLS
# export CK_REPOS=$HOME/CK_REPOS

# The model name determines both the local source files and the remote destination directory.
LOG_ENTRY=`grep "MODEL_NAME" ${CK_DNNC_OUTPUT_DIR}/${CK_DNNC_LOG_FILE}`
MODEL_NAME=`cut -d "=" -f2 <<< ${LOG_ENTRY}`

SRC_DIR=`ck find program:caffe2deephi`/tmp/${CK_DNNC_OUTPUT_DIR}

SSH_CMD="ssh -p ${CK_BOARD_PORT} -l ${CK_BOARD_USER} ${CK_BOARD_ADDRESS}"
ELF_DIR=$(${SSH_CMD} "source ~/.bash_profile; ck find program:image-classification-${MODEL_NAME}-deephi")/elf
DST_DIR="${CK_BOARD_USER}@${CK_BOARD_ADDRESS}:${ELF_DIR}"

# Create the remote destination directory if it doesn't exist.
${SSH_CMD} mkdir -p ${ELF_DIR}

echo "Listing '${DST_DIR}'..."
${SSH_CMD} ls -la ${ELF_DIR}
echo
echo "Copying '${SRC_DIR}/dpu_${MODEL_NAME}*.elf' to '${DST_DIR}'..."
scp -P ${CK_BOARD_PORT} ${SRC_DIR}/dpu_${MODEL_NAME}*.elf ${DST_DIR}
if [ "${?}" != "0" ] ; then
  echo "Error: copy failed!"
  exit 1
fi
echo
echo "Listing '${DST_DIR}'..."
${SSH_CMD} ls -la ${ELF_DIR}
