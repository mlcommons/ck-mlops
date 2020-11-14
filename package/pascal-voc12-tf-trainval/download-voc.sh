#! /bin/bash

# PACKAGE_DIR
# INSTALL_DIR

cd ${INSTALL_DIR}
mkdir dataset

voc2012="VOCtrainval_11-May-2012.tar"
if ! [ -e $voc2012 ]
then
    echo $voc2012 "not found, downloading"
    wget http://host.robots.ox.ac.uk/pascal/VOC/voc2012/$voc2012
fi

# the result is VOCdevkit/VOC2012
tar -xvf VOCtrainval_11-May-2012.tar

cd dataset
pwd

export PYTHONPATH=../source/:$PYTHONPATH

"${CK_ENV_COMPILER_PYTHON_FILE}" create_pascal_tf_record.py \
    --label_map_path=pascal_label_map.pbtxt \
    --data_dir=VOCdevkit --year=VOC2012 --set=train \
    --output_path=pascal_train_2012.record

"${CK_ENV_COMPILER_PYTHON_FILE}" create_pascal_tf_record.py \
    --label_map_path=pascal_label_map.pbtxt \
    --data_dir=VOCdevkit --year=VOC2012 --set=val \
    --output_path=pascal_val_2012.record
