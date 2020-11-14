#!/bin/bash

##env vars
target_folder='/data/emanuele/prova/acc_opencv_ubuntu18_13sept'
ck_repo_folder='/home/emanuele/cck'
######model list

model=('lowproposals,rcnn,resnet50' 'lowproposals,rcnn,resnet101' 'lowproposals,nas,rcnn,vcoco' 'inception-resnet-v2,lowproposals,rcnn' 'ssd,fpn,mobilenet-v1' 'ssd,mobilenet-v1,quantized,mlperf,tf' 'ssd,mobilenet-v1,mlperf,non-quantized,tf' 'ssd,resnet50,fpn' 'ssd,inception-v2' 'ssdlite,mobilenet-v2,vcoco' 'rcnn,inception-v2' 'yolo-v3')
model_tags=('rcnn-resnet50-lowproposals' 'rcnn-resnet101-lowproposals' 'rcnn-nas-lowproposals' 'rcnn-inception-resnet-v2-lowproposals' 'ssd-mobilenet-v1-fpn' 'ssd-mobilenet-v1-quantized-mlperf' 'ssd-mobilenet-v1-non-quantized-mlperf' 'ssd-resnet50-fpn' 'ssd-inception-v2' 'ssdlite-mobilenet-v2' 'rcnn-inception-v2' 'yolo-v3')

##all models there but the rcnn nas non lowproposals, cause it takes too much to evaluate
#model=('rcnn,nas,non-lowproposals' )
#model_tags=('rcnn-nas-non-lowproposals' )


####### accuracy: test only one vm (cuda, basic) with 5k, all models, different image sizes. 
# hypothesis is that accuracy is not changing across libraries. has to be verified. especially for tf.

batch_size=1
batch_count=5000
vm='object-detection-tf-py.tensorrt.ubuntu-18.04'
mod_len=${#model[@]}
#
#non batched


##### normal run, now i only need the yolo
for j in $(seq 1 $mod_len); do
	is_custom=0
	if [ "${model[$j-1]}"  = "yolo-v3" ]; then
		is_custom=1
	fi
		docker run --runtime=nvidia --env-file  $ck_repo_folder/ck-object-detection/docker/object-detection-tf-py.tensorrt.ubuntu-18.04/env.list --user=$(id -u):1500 -v $target_folder:/home/dvdt/CK_REPOS/local/experiment --rm ctuning/${vm} "ck benchmark program:object-detection-tf-py --dep_add_tags.weights=${model[$j-1]} --dep_add_tags.lib-tensorflow=vcuda --repetitions=1 --env.CK_CUSTOM_MODEL=${is_custom} --env.CK_METRIC_TYPE=COCO --env.CK_ENABLE_BATCH=0 --env.CK_BATCH_SIZE=${batch_size} --env.CK_BATCH_COUNT=${batch_count} --env.CK_TF_GPU_MEMORY_PERCENT=99 --record --record_repo=local --record_uoa=mlperf-object-detection-${model_tags[$j-1]}-tf-py-accuracy-no-batch --tags=${model_tags[$j-1]},no-resize"
done

#batched
	for j in $(seq 1 $mod_len); do
		is_custom=0
		if [ "${model[$j-1]}"  = "yolo" ]; then
			is_custom=1
		fi
		docker run --runtime=nvidia --env-file  $ck_repo_folder/ck-object-detection/docker/object-detection-tf-py.tensorrt.ubuntu-18.04/env.list --user=$(id -u):1500 -v $target_folder:/home/dvdt/CK_REPOS/local/experiment --rm ctuning/${vm} "ck benchmark program:object-detection-tf-py --dep_add_tags.weights=${model[$j-1]} --repetitions=1 --dep_add_tags.lib-tensorflow=vcuda --env.CK_CUSTOM_MODEL=${is_custom} --env.CK_BATCH_SIZE=${batch_size} --env.CK_BATCH_COUNT=${batch_count} --env.CK_TF_GPU_MEMORY_PERCENT=99 --env.CK_METRIC_TYPE=COCO --env.CK_ENABLE_BATCH=1 --record --record_repo=local --record_uoa=mlperf-object-detection-${model_tags[$j-1]}-tf-py-accuracy-model-width-height --tags=${model_tags[$j-1]},model-resize"
	done


