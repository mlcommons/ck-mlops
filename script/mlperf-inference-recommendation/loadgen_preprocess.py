#
# MLPerf inference; recommendation; preprocessing
#
# Copyright (c) 2019 cTuning foundation.
# Copyright (c) 2021 OctoML, Inc.
#
# Developers:
# - Grigori Fursin, OctoML, 2021
#

import json
import os
import re

def ck_preprocess(i):

    # Set working vars
    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    env=i['env']
    new_env={} # new environment to be added to the run script
    bat='\n'

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']
    remote=tosd.get('remote','')

    # Get model name from a CK package in MLPerf loadgen format
    ml_model_env = deps['model']['dict']['env']
    ml_model_install_env = deps['model']['dict']['customize']['install_env']

    # Get DLRM path
    dlrm_env = deps['tool-dlrm']['dict']['env']

    path_to_dlrm = dlrm_env.get('CK_ENV_TOOL_DLRM', '')

    new_env['DLRM_DIR'] = path_to_dlrm

    # Get dataset (can be Criteo Terabyte or Kaggle DAC)
    dataset_env=deps['dataset']['dict']['env']
    dataset_install_env = deps['dataset']['dict']['customize']['install_env']

    path_to_dataset=dataset_env.get('CK_ENV_DATASET_CRITEO_TERABYTE', '')
    if path_to_dataset=='':
        path_to_dataset=dataset_env.get('CK_ENV_DATASET_KAGGLE_DAC', '')

    new_env['DATA_DIR']=path_to_dataset
    new_env['CK_ENV_DATASET_ROOT']=path_to_dataset

    # Update MLPERF_PROFILE

    mlperf_model_name=ml_model_install_env.get('MLPERF_MODEL_NAME', 'dlrm')

    # Check if MLPERF_DATASET
    mlperf_dataset=env.get('MLPERF_DATASET','')
    if mlperf_dataset=='':
        mlperf_dataset=dataset_install_env.get('MLPERF_DATASET','')

    mlperf_profile=ml_model_env.get('MLPERF_PROFILE','')
    if mlperf_profile=='': mlperf_profile=mlperf_model_name+'-'+mlperf_dataset
    new_env['MLPERF_PROFILE']=mlperf_profile

    # Check extra opts
    opts=env.get('CK_LOADGEN_OPTS','')

    # Add --dataset
    if mlperf_dataset!='':
        opts+=' --dataset '+mlperf_dataset

    # Check output directory
    opts+=' --output '+os.getcwd()

    # Use model name
    opts+=' --model '+mlperf_model_name

    # Check if force external model (testing and open division) or use standard name
    model_path=env.get('ML_MODEL_FILEPATH_EXTERNAL','')
    if model_path=='':
       # Check model name from a CK package
       model_path=ml_model_env.get('ML_MODEL_FILEPATH','')
    if model_path!='':
        opts+=' --model-path '+model_path

    # Recommendation dataset/model size customization
    if mlperf_dataset=='terabyte':
        max_ind_range=ml_model_install_env.get('MLPERF_MAX_IND_RANGE','')
        if max_ind_range!='':
            opts+=' --max-ind-range '+max_ind_range
        data_sub_sample_rate=ml_model_install_env.get('MLPERF_DATA_SUB_SAMPLE_RATE','')
        if data_sub_sample_rate!='':
            opts+=' --data-sub-sample-rate '+data_sub_sample_rate

    # Use MLPerf binary loader if specified via --env.MLPERF_USE_BIN_LOADER="yes"
    use_mlperf_bin_loader=env.get('MLPERF_USE_BIN_LOADER','')
    if use_mlperf_bin_loader.lower()=='yes':
        opts+=' --mlperf-bin-loader'

    # Use --use-gpu if MLPERF_DEVICE is GPU
    mlperf_device=env.get('MLPERF_DEVICE','')
    if mlperf_device.lower()=='gpu':
        opts+=' --use-gpu'

    # Other options configurable via --env.EXTRA_OPS:
    # --test-num-workers --find-peak-performance --threads
    # --duration --target-qps --max-latency --count-samples --count-queries
    # --samples-per-query-multistream --samples-per-query-offline
    # --samples-to-aggregate-fix --samples-to-aggregate-min --samples-to-aggregate-max --samples-to-aggregate-quantile-file --samples-to-aggregate-trace-file
    # --numpy-rand-seed

    # Call common script and finalize opts and env
    i['loadgen_opts']=opts

    # Call common script
    i['script_data_uoa']='2405d9faf8d788ae' # script:mlperf-inference-recommendation

    r=ck.access({'action':'run', 'module_uoa':'script', 'data_uoa':'mlperf-inference', 
                 'code':'loadgen_common', 'func':'ck_preprocess', 
                 'dict':i})
    if r['return']>0: return r
    new_env.update(r['new_env'])

    return {'return':0, 'bat':bat, 'new_env':new_env}

# Do not add anything here!
