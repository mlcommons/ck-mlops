#! /bin/bash

# PACKAGE_DIR
# INSTALL_DIR

cd ${INSTALL_DIR}

mkdir -p t2t_data
pwd

"${CK_ENV_COMPILER_PYTHON_FILE}"  ./source/tensor2tensor/tensor2tensor/bin/t2t-datagen.py \
  --data_dir=t2t_data \
  --problem=translate_ende_wmt32k

