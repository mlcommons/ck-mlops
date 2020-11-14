#!/bin/bash

### paths here
target_folder='/data/emanuele/prova/check_out_trtdyn_int8'
ck_repo_folder='/home/emanuele/cck'
vm='object-detection-tf-py.tensorrt.ubuntu-18.04'


######model list

model=( 'lowproposals,nas,rcnn,vcoco' 'inception-resnet-v2,lowproposals,rcnn' )
#model=('lowproposals,rcnn,resnet50' 'lowproposals,rcnn,resnet101' 'lowproposals,nas,rcnn,vcoco' 'inception-resnet-v2,lowproposals,rcnn' 'ssd,fpn,mobilenet-v1' 'ssd,mobilenet-v1,quantized,mlperf,tf' 'ssd,mobilenet-v1,mlperf,non-quantized,tf' 'ssd,resnet50,fpn' 'ssd,inception-v2' 'ssdlite,mobilenet-v2,vcoco' 'rcnn,inception-v2' 'yolo-v3')
model_tags=('rcnn-nas-lowproposals' 'rcnn-inception-resnet-v2-lowproposals' )
#model_tags=('rcnn-resnet50-lowproposals' 'rcnn-resnet101-lowproposals' 'rcnn-nas-lowproposals' 'rcnn-inception-resnet-v2-lowproposals' 'ssd-mobilenet-v1-fpn' 'ssd-mobilenet-v1-quantized-mlperf' 'ssd-mobilenet-v1-non-quantized-mlperf' 'ssd-resnet50-fpn' 'ssd-inception-v2' 'ssdlite-mobilenet-v2' 'rcnn-inception-v2' 'yolo-v3')

mod_len=${#model[@]}


####### performances: test all possible configurations, 10 times, all models, different batch sizes. 

##batch info
batch_size=( 1 2 4 8 16 32 )
batch_count=2    
bat_len=${#batch_size[@]}

##config info
#configs=('--dep_add_tags.lib-tensorflow=vcpu' '--dep_add_tags.lib-tensorflow=vcuda --env.CUDA_VISIBLE_DEVICES=-1' '--dep_add_tags.lib-tensorflow=vcuda' '--dep_add_tags.lib-tensorflow=vcuda --env.CK_ENABLE_TENSORRT=1' '--dep_add_tags.lib-tensorflow=vcuda --env.CK_ENABLE_TENSORRT=1 --env.CK_TENSORRT_DYNAMIC=1')
configs=('--dep_add_tags.lib-tensorflow=vcuda --env.CK_ENABLE_TENSORRT=1 --env.CK_TENSORRT_DYNAMIC=1')
#config_tags=('cpu-prebuilt' 'cpu' 'cuda' 'tensorrt' 'tensorrt-dynamic')
config_tags=( 'tensorrt-dynamic')
config_len=${#configs[@]}


for bs in $(seq 1 $bat_len); do  
	for k in $(seq 1 $config_len); do	
		for j in $(seq 1 $mod_len); do
			is_custom=0
			if [ "${model[$j-1]}"  = "yolo-v3" ]; then
				is_custom=1
			fi
			docker run --runtime=nvidia --env-file  $ck_repo_folder/ck-object-detection/docker/object-detection-tf-py.tensorrt.ubuntu-18.04/env.list --user=$(id -u):1500 -v $target_folder:/home/dvdt/CK_REPOS/local/experiment --rm ctuning/${vm} "ck benchmark program:object-detection-tf-py --dep_add_tags.weights=${model[$j-1]} --repetitions=10 --env.CK_CUSTOM_MODEL=${is_custom} --env.CK_BATCH_SIZE=${batch_size[$bs-1]} --env.CK_BATCH_COUNT=${batch_count} --env.CK_TF_GPU_MEMORY_PERCENT=99 --env.CK_METRIC_TYPE=COCO --env.CK_ENABLE_BATCH=1 ${configs[$k-1]}  --record --record_repo=local --record_uoa=mlperf-object-detection-${model_tags[$j-1]}-tf-py-performance-${config_tags[$k-1]}-batch-size${batch_size[$bs-1]} --tags=${config_tags[$k-1]},${model_tags[$j-1]}"
		done
	done
done


#--env.CK_TENSORRT_PRECISION='INT8'
