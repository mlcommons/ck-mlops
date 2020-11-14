#!/bin/bash

### paths here
repo_name='bla'

######model list

#model=('lowproposals,rcnn,resnet50' 'lowproposals,rcnn,resnet101' 'lowproposals,nas,rcnn,vcoco' 'inception-resnet-v2,lowproposals,rcnn' 'ssd,fpn,mobilenet-v1' 'ssd,mobilenet-v1,quantized,mlperf,tf' 'ssd,mobilenet-v1,mlperf,non-quantized,tf' 'ssd,resnet50,fpn' 'ssd,inception-v2' 'ssdlite,mobilenet-v2,vcoco' 'rcnn,inception-v2' 'yolo-v3')
#model_tags=('rcnn-resnet50-lowproposals' 'rcnn-resnet101-lowproposals' 'rcnn-nas-lowproposals' 'rcnn-inception-resnet-v2-lowproposals' 'ssd-mobilenet-v1-fpn' 'ssd-mobilenet-v1-quantized-mlperf' 'ssd-mobilenet-v1-non-quantized-mlperf' 'ssd-resnet50-fpn' 'ssd-inception-v2' 'ssdlite-mobilenet-v2' 'rcnn-inception-v2' 'yolo-v3')
model=('yolo-v3')
#model=('ssd,mobilenet-v1,quantized,mlperf,tf' 'yolo-v3'  )
#model_tags=('ssd-mobilenet-v1-quantized-mlperf' 'yolo-v3' )
model_tags=('yolo-v3')

mod_len=${#model[@]}


####### performances: test all possible configurations, 10 times, all models, different batch sizes. 

##batch info
batch_size=( 20 )
#batch_size=( 2 )
batch_count=1    
bat_len=${#batch_size[@]}

##config info (backend tf lib)
configs=(
#'--dep_add_tags.lib-tensorflow=vcuda,vsrc --env.CUDA_VISIBLE_DEVICES=-1'
#'--dep_add_tags.lib-tensorflow=vcuda,vsrc '
'--dep_add_tags.lib-tensorflow=vcuda,vsrc '
'--dep_add_tags.lib-tensorflow=vcuda,vsrc  --env.CK_TENSORRT_DYNAMIC=1'

 )
config_tags=(
# 'cpu' 'cuda'
 'tensorrt' 'tensorrtdyn')
config_len=${#config_tags[@]}



##config #2 (scenario)
#scenarios=('--env.CK_SCENARIO=SingleStream' '--env.CK_SCENARIO=MultiStream' '--env.CK_SCENARIO=Server' '--env.CK_SCENARIO=Offline')
scenarios=( '--env.CK_SCENARIO=Offline')
#scenarios_tags=('SingleStream' 'MultiStream' 'Server' 'Offline')
scenarios_tags=( 'Offline')
scenarios_len=${#scenarios[@]}


#config #3 (ck profile)





for bs in $(seq 1 $bat_len); do
	for k in $(seq 1 $config_len); do	
		for j in $(seq 1 $mod_len); do
			for sc in $(seq 1 $scenarios_len); do
				profile='default_tf_object_det_zoo'
				if [ "${model[$j-1]}"  = "yolo-v3" ]; then
					if [ "${config_tags[$k-1]}" = 'tensorrt' ] || [ "${config_tags[$k-1]}" = 'tensorrtdyn' ]; then
						profile='tf_yolo_trt'
					else 
						profile='tf_yolo'
					fi
				else
					if [ "${config_tags[$k-1]}" = 'tensorrt' ] || [ "${config_tags[$k-1]}" = 'tensorrtdyn' ] 
						then
						profile='default_tf_trt_object_det_zoo'
					fi
				fi
				ck benchmark program:mlperf-inference-vision --dep_add_tags.weights=${model[$j-1]} --dep_add_tags.dataset=coco,full,v2017,val --dep_add_tags.lib-python-matplotlib=v3.1 --dep_add_tags.lib-python-numpy=v1.16 --dep_add_tags.python=v3.6 --repetitions=1 --env.CK_PROFILE=${profile} --env.CK_BATCH_SIZE=${batch_size[$bs-1]} --env.CK_BATCH_COUNT=${batch_count} --env.CK_TF_GPU_MEMORY_PERCENT=99 --env.CK_METRIC_TYPE=COCO --env.CK_ENABLE_BATCH=1 ${configs[$k-1]} --skip_print_timers --skip_stat_analysis --process_multi_keys --record --record_repo=${repo_name} --record_uoa=${model_tags[$j-1]}-${config_tags[$k-1]}-${scenarios_tags[$sc-1]}-batch-size${batch_size[$bs-1]} --tags=${config_tags[$k-1]},${model_tags[$j-1]},${scenarios_tags[$sc-1]}
			done
		done
	done
done
