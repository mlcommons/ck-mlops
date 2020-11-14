#
# Convert raw output of a typical DeePhi program to the CK format.
#
# See CK LICENSE.txt for licensing details.
# See CK COPYRIGHT.txt for copyright details.
#
# Developer: Anton Lokhmotov.
#

#
# Sample raw output:
#
# Load image : ILSVRC2012_val_00000001.JPEG
# top[0] prob = 0.714799  name = n01737021 water snake
# top[1] prob = 0.096738  name = n01744401 rock python, rock snake, Python sebae
# top[2] prob = 0.075339  name = n01729322 hognose snake, puff adder, sand viper
# top[3] prob = 0.035588  name = n01751748 sea snake
# top[4] prob = 0.013092  name = n01748264 Indian cobra, Naja naja
# Profiling info:
#   DPU CONV Execution time: 18061us
#   DPU CONV Performance: 426.887GOPS
#   DPU FC Execution time: 417us
#   DPU FC Performance: 9.59233GOPS
#   WALLCLOCK LOAD Execution time: 18179us
#   WALLCLOCK CONV Execution time: 18714us
#   WALLCLOCK AVGPOOL Execution time: 4985us
#   WALLCLOCK FC Execution time: 435us
#   WALLCLOCK INT8->FP32 Execution time: 29us
#   WALLCLOCK SOFTMAX Execution time: 110us
#   WALLCLOCK TOTAL Execution time: 42452us
#

import json
import os
import re

def ck_postprocess(i):

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']


    d={}
    d['frame_predictions'] = []
    d['batch_performance_fps'] = []
    d['batch_duration_us'] = []
    d['debug']=rt['params'].get('debug','no')

    # Collect deps of interest.
    imagenet_val=deps.get('dataset-imagenet-val',{})
    imagenet_val_dict=imagenet_val.get('dict',{})
    imagenet_val_dict_env=imagenet_val_dict.get('env',{})
    d['CK_CAFFE_IMAGENET_VAL']=imagenet_val_dict_env.get('CK_CAFFE_IMAGENET_VAL','')

    imagenet_aux=deps.get('dataset-imagenet-aux',{})
    imagenet_aux_dict=imagenet_aux.get('dict',{})
    imagenet_aux_dict_env=imagenet_aux_dict.get('env',{})
    d['CK_CAFFE_IMAGENET_VAL_TXT']=imagenet_aux_dict_env.get('CK_CAFFE_IMAGENET_VAL_TXT','')
    if d['CK_CAFFE_IMAGENET_VAL_TXT']!='':
        with open(d['CK_CAFFE_IMAGENET_VAL_TXT']) as imagenet_val_txt:
            image_to_synset_map = {}
            for image_synset in imagenet_val_txt:
                (image, synset) = image_synset.split()
                image_to_synset_map[image] = int(synset)
    d['CK_CAFFE_IMAGENET_SYNSET_WORDS_TXT']=imagenet_aux_dict_env.get('CK_CAFFE_IMAGENET_SYNSET_WORDS_TXT','')
    if d['CK_CAFFE_IMAGENET_SYNSET_WORDS_TXT']!='':
        with open(d['CK_CAFFE_IMAGENET_SYNSET_WORDS_TXT']) as imagenet_synset_words_txt:
            synset_list = imagenet_synset_words_txt.read().splitlines()

    # Load stdout as list.
    rf1=rt['run_cmd_out1']
    lst=[]
    if os.path.isfile(rf1):
        r=ck.load_text_file({'text_file':rf1,'split_to_list':'yes'})
        if r['return']>0: return r
        lst+=r['lst']

    # Match e.g. 'Load image : ILSVRC2012_val_00000001.JPEG'.
    image_regex = '((Load\s+image)|(Image\s+[n|N]ame))\s*:\s*' + \
         '(?P<file_name>.*)'

    # Match e.g. 'WALLCLOCK INT8->FP32 Execution time: 18020us'.
    time_regex = \
        '(?P<ty>\w+) ' + \
        '(?P<op>[\w\-\>]+) ' + \
        'Execution time: ' + \
        '(?P<us>\d+)us'

    # Match e.g. 'DPU FC Performance: 9.63855GOPS'
    performance_regex = \
        'DPU ' + \
        '(?P<op>\w+) ' + \
        'Performance: ' + \
        '(?P<gops>\d*\.?\d*)GOPS'

    # Match e.g. 'top[0] prob = 0.714799  name = n01737021 water snake'
    pos_prob_name_regex = \
        'top\[(?P<pos>\d+)\]\s+' + \
        'prob = (?P<prob>\d*\.?\d*)\s+' + \
        'name = (?P<name>.*)'

    # Match metrics from template e.g.
    # BATCH Duration: 1316318 us
    # BATCH Performance: 379.847 FPS
    duration_regex = \
        '(?P<batch_or_total>(BATCH|TOTAL))\s+Duration\s*:\s+' + \
        '(?P<duration>\d*)\s*us'
    fps_regex = \
        '(?P<batch_or_total>(BATCH|TOTAL))\s+Performance\s*:\s+' + \
        '(?P<fps>\d*\.?\d*)\s*FPS'

    # Current frame prediction.
    frame_prediction = {}

    for line in lst:
        match = re.search(image_regex, line)
        # Start next frame.
        if match:
            # Append info for previous frame.
            if frame_prediction: d['frame_predictions'].append(frame_prediction)
            # Reset frame prediction.
            frame_prediction = {}
            frame_prediction['file_name'] = match.group('file_name')
            frame_prediction['execution_time_us'] = {}
            frame_prediction['performance_gops']    = {}
            frame_prediction['prediction']  = []
            frame_prediction['class_correct'] = image_to_synset_map.get(frame_prediction['file_name'], -1)

        match = re.search(time_regex, line)
        if match:
            ty = match.group('ty')
            op = match.group('op')
            us = match.group('us')
            frame_prediction['execution_time_us'][ty+' '+op] = int(us)

        match = re.search(performance_regex, line)
        if match:
            op = match.group('op')
            gops = match.group('gops')
            frame_prediction['performance_gops'][op] = float(gops)

        match = re.search(pos_prob_name_regex, line)
        if match:
            prediction = {}
            prediction['pos'] = int(match.group('pos'))
            prediction['prob'] = match.group('prob')
            prediction['name'] = match.group('name')
            prediction['class'] = synset_list.index(prediction['name'])
            frame_prediction['prediction'].append(prediction)

        match = re.search(duration_regex, line)
        if match:
            duration = int(match.group('duration'))
            batch_or_total = match.group('batch_or_total')
            if batch_or_total=='BATCH':
                d['batch_duration_us'].append(duration)
            elif batch_or_total=='TOTAL':
                d['total_duration_us'] = duration

        match = re.search(fps_regex, line)
        if match:
            fps = float(match.group('fps'))
            batch_or_total = match.group('batch_or_total')
            if batch_or_total=='BATCH':
                d['batch_performance_fps'].append(fps)
            elif batch_or_total=='TOTAL':
                d['total_performance_fps'] = fps

    # Append the last collected frame prediction.
    d['frame_predictions'].append(frame_prediction)

    d['post_processed']='yes'

    top_n_list = [1,5]
    for n in top_n_list:
        top_n_accuracy = 'accuracy_top'+str(n)
        d[top_n_accuracy] = 0

    # Calculate accuracy per frame.
    for frame_prediction in d['frame_predictions']:
        for n in top_n_list:
            top_n_accuracy = 'accuracy_top'+str(n)
            frame_prediction[top_n_accuracy] = 'no'
        for prediction_entry in frame_prediction['prediction']:
            if prediction_entry['class']==frame_prediction['class_correct']:
                for n in top_n_list:
                    if prediction_entry['pos'] < n:
                        top_n_accuracy = 'accuracy_top'+str(n)
                        frame_prediction[top_n_accuracy] = 'yes'
                        d[top_n_accuracy] += 1

    # Calculate total wallclock, compute wallclock and DPU profiling time.
    total_time_us = 0
    compute_time_us = 0
    dpu_time_us = 0
    for frame_prediction in d['frame_predictions']:
        execution_time_us = frame_prediction['execution_time_us']
        for k,v in execution_time_us.items():
            if k.find('TOTAL')!=-1:
                total_time_us += v
            if k.find('COMPUTE')!=-1:
                compute_time_us += v
            if k.startswith('DPU'):
                dpu_time_us += v

    rr={}
    rr['return']=0
    if d.get('post_processed','')=='yes':
        # Calculate the overall accuracy.
        num_images = len(d['frame_predictions'])
        scaling = 1.0 / num_images
        for n in top_n_list:
             top_n_accuracy = 'accuracy_top'+str(n)
             d[top_n_accuracy] *= scaling
        # Calculate average execution times.
        d['average_dpu_time_us'] = int(dpu_time_us * scaling)
        d['average_compute_time_us'] = int(compute_time_us * scaling)
        d['average_total_time_us'] = int(total_time_us * scaling)
        d['execution_time'] = total_time_us * scaling * 1e-6
        # For template, output total duration in seconds.
        if d['execution_time']==0: d['execution_time'] = d['total_duration_us'] * 1e-6

        # Remove frame predictions for non-debug output.
        if d['debug']=='no':
            del d['frame_predictions']
        # Save to file.
        r=ck.save_json_to_file({'json_file':rt['fine_grain_timer_file'], 'dict':d})
        if r['return']>0: return r
    else:
        rr['return']=1
        rr['error']='failed to match DeePhi output'

    return rr

# Do not add anything here!
