#! /bin/bash

# PACKAGE_DIR
# INSTALL_DIR

cd ${INSTALL_DIR}
mkdir dataset

declare -a arr=("VOCtrainval_06-Nov-2007.tar")
for i in "${arr[@]}"
do
    if ! [ -e $i ]
    then
        echo $i "not found, downloading"
        wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/$i
    fi
done

# the result is VOCdevkit/VOC2012
tar -xvf VOCtrainval_06-Nov-2007.tar

cd dataset
pwd

export PYTHONPATH=../source/:$PYTHONPATH

"${CK_ENV_COMPILER_PYTHON_FILE}" create_pascal_tf_record.py \
    --label_map_path=pascal_label_map.pbtxt \
    --data_dir=VOCdevkit --year=VOC2007 --set=train \
    --output_path=pascal_train_2007.record

"${CK_ENV_COMPILER_PYTHON_FILE}" create_pascal_tf_record.py \
    --label_map_path=pascal_label_map.pbtxt \
    --data_dir=VOCdevkit --year=VOC2007 --set=val \
    --output_path=pascal_val_2007.record
