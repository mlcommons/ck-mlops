#
# MLPerf inference; image classification; preprocessing
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

    if remote=='yes':
       es=tosd['env_set']
    else:
       es=hosd['env_set'] # set or export

    ###############################################################################
    # Specific for COCO

    # TBD - must be more flexible and does not depend on COCO
    #   can be other data sets ...

    path_to_dataset=deps['dataset']['dict']['env']['CK_ENV_DATASET_COCO']
    new_env['DATA_DIR']=path_to_dataset

    ###############################################################################
    # Prepare options for loadgen based on env vars

    # Call common script
    i['script_data_uoa']='53bb701c440aaa69' # script:mlperf-inference-object-detection

    r=ck.access({'action':'run', 'module_uoa':'script', 'data_uoa':'mlperf-inference', 
                 'code':'loadgen_common_vision', 'func':'ck_preprocess', 
                 'dict':i})
    if r['return']>0: return r
    new_env.update(r['new_env'])

    return {'return':0, 'bat':bat, 'new_env':new_env}

# Do not add anything here!
