#!/usr/bin/python

#
# Developers:
# - Anton Lokhmotov, anton@dividiti.com
# - Gavin Simpson, gavin.s.simpson@gmail.com
#

import os
import sys
import json
import re
from pathlib import Path

################################################################################
# OpenVINO configuration file template.
# Original: https://raw.githubusercontent.com/mlperf/inference_results_v0.5/master/closed/Intel/calibration/OV_RN-50-sample/resnet_v1.5_50.yml
template = \
'''
models:
  - name: %(name)s
    launchers:
      - framework: dlsdk
        device: CPU
        tf_model: %(tf_model)s
        adapter: classification
        mo_params:
          data_type: %(data_type)s
          input_shape: (%(batch_size)d, %(height)d, %(width)d, %(channels)d)
          output: %(output)s
        cpu_extensions: AUTO
    datasets:
      - name: ImageNet2012_bkgr
        data_source: %(data_source)s
        annotation: %(install_path)s/imagenet.pickle
        dataset_meta: %(install_path)s/imagenet.json
        annotation_conversion:
          converter: imagenet
          annotation_file: %(annotation_file)s
          labels_file: %(labels_file)s
          has_background: %(has_background)s
        subsample_size: 500
        preprocessing:
          - type: resize
            size: 256
            aspect_ratio_scale: %(aspect_ratio_scale)s
          - type: crop
            size: 224
          - type: normalization
            mean: %(mean)s
            std: %(std)s
        metrics:
          - name: accuracy @ top1
            type: accuracy
            top_k: 1
'''

def get_config_file(i):
    ck=i['ck_kernel']
    deps=i['deps']
    install_path = i['install_path']
    install_env = i['cfg']['customize']['install_env']

    model_env = deps['model-source']['dict']['env']
    if install_env.get('CK_OPENVINO_PREPROCESSING_MEAN','') != '':
        mean = re.sub("\s+", ",", install_env['CK_OPENVINO_PREPROCESSING_MEAN'].strip())
    elif model_env.get('ML_MODEL_GIVEN_CHANNEL_MEANS','') != '':
        mean = re.sub("\s+", ",", model_env['ML_MODEL_GIVEN_CHANNEL_MEANS'].strip())
    else:
        mean = ''
    std = install_env.get('CK_OPENVINO_PREPROCESSING_STD', '')

    aux_env = deps['imagenet-aux']['dict']['env']
    imc_env = deps['imagenet-cal']['dict']['env']

    return template % {
        "name"               : model_env['CK_ENV_TENSORFLOW_MODEL_NAME'],
        "tf_model"           : model_env['CK_ENV_TENSORFLOW_MODEL_TF_FROZEN_FILEPATH'],
        "output"             : model_env['CK_ENV_TENSORFLOW_MODEL_OUTPUT_LAYER_NAME'],
        "data_type"          : install_env.get('CK_OPENVINO_MO_PARAMS_DATA_TYPE','FP32'),
        "batch_size"         : 1,
        "height"             : int(model_env['CK_ENV_TENSORFLOW_MODEL_IMAGE_HEIGHT']),
        "width"              : int(model_env['CK_ENV_TENSORFLOW_MODEL_IMAGE_HEIGHT']),
        "channels"           : 3,
        "has_background"     : install_env.get('CK_OPENVINO_ANNOTATION_CONVERSION_HAS_BACKGROUND','False'),
        "aspect_ratio_scale" : install_env.get('CK_OPENVINO_PREPROCESSING_ASPECT_RATIO_SCALE',''),
        "mean"               : mean,
        "std"                : std,
        "data_source"        : imc_env['CK_DATASET_IMAGENET_CALIBRATION_ROOT'],
        "labels_file"        : aux_env['CK_CAFFE_IMAGENET_SYNSET_WORDS_TXT'],
        "annotation_file"    : imc_env['CK_DATASET_IMAGENET_CALIBRATION_VAL_MAP_PATH'],
        "install_path"       : install_path
    }

################################################################################
# customize installation
def setup(i):
    """
    Input:  {
              cfg              - meta of this soft entry
              self_cfg         - meta of module soft
              ck_kernel        - import CK kernel module (to reuse functions)

              host_os_uoa      - host OS UOA
              host_os_uid      - host OS UID
              host_os_dict     - host OS meta

              target_os_uoa    - target OS UOA
              target_os_uid    - target OS UID
              target_os_dict   - target OS meta

              target_device_id - target device ID (if via ADB)

              tags             - list of tags used to search this entry

              env              - updated environment vars from meta
              customize        - updated customize vars from meta

              deps             - resolved dependencies for this soft

              interactive      - if 'yes', can ask questions, otherwise quiet

              path             - path to entry (with scripts)
              install_path     - installation path
            }

    Output: {
              return        - return code =  0, if successful
                                          >  0, if error
              (error)       - error text if return > 0
              (install-env) - prepare environment to be used before the install script
            }

    """

    import os
    import shutil

    # Get variables
    o=i.get('out','')
    ip=i.get('install_path','')

    ck=i['ck_kernel']

    hos=i['host_os_uoa']
    tos=i['target_os_uoa']

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    hname=hosd.get('ck_name','')    # win, linux
    hname2=hosd.get('ck_name2','')  # win, mingw, linux, android
    macos=hosd.get('macos','')      # yes/no

    tname=tosd.get('ck_name','')    # win, linux
    tname2=tosd.get('ck_name2','')  # win, mingw, linux, android

    install_env = i['cfg']['customize']['install_env']
    if install_env.get('CK_CALIBRATE_IMAGENET', '') != '':
        config_file = get_config_file(i)
        ck.out(config_file)
        Path(ip).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(ip, 'config.yml'), 'w') as config_yml:
            config_yml.write(config_file)
    
    return {'return':0}
