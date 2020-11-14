#!/bin/bash

### paths here
repo_name='ck-object-detection'

######model list

#model=('lowproposals,rcnn,resnet50' 'lowproposals,rcnn,resnet101' 'lowproposals,nas,rcnn,vcoco' 'inception-resnet-v2,lowproposals,rcnn' 'ssd,fpn,mobilenet-v1' 'ssd,mobilenet-v1,quantized,mlperf,tf' 'ssd,mobilenet-v1,mlperf,non-quantized,tf' 'ssd,resnet50,fpn' 'ssd,inception-v2' 'ssdlite,mobilenet-v2,vcoco' 'rcnn,inception-v2' 'yolo-v3')
#model_tags=('rcnn-resnet50-lowproposals' 'rcnn-resnet101-lowproposals' 'rcnn-nas-lowproposals' 'rcnn-inception-resnet-v2-lowproposals' 'ssd-mobilenet-v1-fpn' 'ssd-mobilenet-v1-quantized-mlperf' 'ssd-mobilenet-v1-non-quantized-mlperf' 'ssd-resnet50-fpn' 'ssd-inception-v2' 'ssdlite-mobilenet-v2' 'rcnn-inception-v2' 'yolo-v3')
#model=('yolo-v3')
model=('rcnn,nas,lowproposals,vcoco' 'ssd,mobilenet-v1,fpn' 'ssd,mobilenet-v1,quantized,mlperf,tf' 'ssd,resnet50,fpn' 'yolo-v3')
model_tags=('rcnn-nas-lowproposals' 'ssd-mobilenet-v1-fpn' 'ssd-mobilenet-v1-quantized-mlperf' 'ssd-resnet50-fpn'  'yolo-v3')
#model_tags=('yolo-v3')

mod_len=${#model[@]}


####### performances: test all possible configurations, 10 times, all models, different batch sizes. 

##batch info
batch_size=( 1 2 4 8 16 32 )
#batch_size=( 2 )
batch_count=2    
bat_len=${#batch_size[@]}

##config info
configs=('--dep_add_tags.lib-tensorflow=vcpu,vprebuilt,v1.14' '--dep_add_tags.lib-tensorflow=vcpu,vsrc,v1.14' '--dep_add_tags.lib-tensorflow=vcuda,vsrc' '--dep_add_tags.lib-tensorflow=vcuda,vsrc --env.CK_ENABLE_TENSORRT=1' '--dep_add_tags.lib-tensorflow=vcuda,vsrc --env.CK_ENABLE_TENSORRT=1 --env.CK_TENSORRT_DYNAMIC=1')
config_tags=('cpu-prebuilt' 'cpu' 'cuda' 'tensorrt' 'tensorrt-dynamic')
config_len=${#configs[@]}


for bs in $(seq 1 $bat_len); do  
	for k in $(seq 1 $config_len); do	
		for j in $(seq 1 $mod_len); do
			is_custom=0
			if [ "${model[$j-1]}"  = "yolo-v3" ]; then
				is_custom=1
			fi
			ck benchmark program:object-detection-tf-py --dep_add_tags.weights=${model[$j-1]} --dep_add_tags.dataset=coco,full,v2017,val --dep_add_tags.lib-python-matplotlib=v3.1 --dep_add_tags.lib-python-numpy=v1.16 --dep_add_tags.python=v3.6 --repetitions=10 --env.CK_CUSTOM_MODEL=${is_custom} --env.CK_BATCH_SIZE=${batch_size[$bs-1]} --env.CK_BATCH_COUNT=${batch_count} --env.CK_TF_GPU_MEMORY_PERCENT=80 --env.CK_METRIC_TYPE=COCO --env.CK_ENABLE_BATCH=1 ${configs[$k-1]} --record --record_repo=${repo_name} --record_uoa=object-detection-${model_tags[$j-1]}-tf-py-performance-${config_tags[$k-1]}-batch-size${batch_size[$bs-1]} --tags=${config_tags[$k-1]},${model_tags[$j-1]}
		done
	done
done
