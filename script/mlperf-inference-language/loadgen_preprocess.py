#
# MLPerf inference; language; preprocessing
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

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    env=i['env']
    new_env={} # new environment to be added to the run script
    bat='\n'

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']
    remote=tosd.get('remote','')

    # # Get model name from a CK package in MLPerf loadgen format
    ml_model_dict = deps['model']['dict']
    ml_model_env_dict = deps['model']['dict']['env']

    # path_to_squad=deps['dataset']['dict']['env']['CK_ENV_DATASET_SQUAD_DEV']
    # path_to_squad_dev=os.path.join(path_to_squad, 'dev-v1.1.json')

    # Check extra opts
    opts=env.get('CK_LOADGEN_OPTS','')

    # Check max examples
    max_examples=env.get('CK_LOADGEN_MAX_EXAMPLES','')
    if max_examples:
        opts+=' --max_examples='+max_examples

    if ml_model_env_dict.get('MLPERF_MODEL_QUANTIZED','').lower()=='yes':
        opts+=' --quantized'

    if env.get('CK_MLPERF_PROFILE','').lower()=='yes':
        opts+=' --profile'

    # Check output directory
    new_env['CK_MLPERF_OUTPUT_DIR']=os.getcwd()

    ###############################################################################
    # Prepare options for loadgen based on env vars

    i['script_data_uoa']='80cd847d1831aed2' # script:mlperf-inference-language
    i['loadgen_opts']=opts

    r=ck.access({'action':'run', 'module_uoa':'script', 'data_uoa':'mlperf-inference', 
                 'code':'loadgen_common', 'func':'ck_preprocess', 
                 'dict':i})
    if r['return']>0: return r

    new_env.update(r['new_env'])

    return {'return':0, 'bat':bat, 'new_env':new_env}

# Do not add anything here!
