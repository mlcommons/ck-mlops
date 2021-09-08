#
# MLPerf inference; common preprocessing
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

    ###############################################################################
    # Prepare options for loadgen based on env vars

    # Check extra opts
    opts=i.get('loadgen_opts','')

    # Check if MLPERF_BACKEND is not the same if MLPERF_PROFILE_BACKEND
    mlperf_backend=env['MLPERF_BACKEND']
    mlperf_profile_backend=env.get('MLPERF_PROFILE_BACKEND','')

    if mlperf_profile_backend=='':
       new_env['MLPERF_PROFILE_BACKEND']=mlperf_backend
    else:
       opts='--backend '+mlperf_backend+' '+opts

    # Check accuracy
    accuracy=env.get('CK_LOADGEN_ACCURACY','').lower()=='on'
    if accuracy:
        opts='--accuracy '+opts

    # Set extra options for LOADGEN
    opts=opts.strip()
    new_env['CK_LOADGEN_ASSEMBLED_OPTS']=opts

    script_data_uoa=i['script_data_uoa']

    # Find path for shared scripts for a given task
    r=ck.access({'action': 'find', 'module_uoa': 'script', 'data_uoa': script_data_uoa})
    if r['return']>0: return r
    p=r['path']

    new_env['CK_PATH_TO_COMMON_SCRIPT']=p

    # Find path for shared scripts for MLPerf
    r=ck.access({'action': 'find', 'module_uoa': 'script', 'data_uoa': 'mlperf-inference'})
    if r['return']>0: return r
    p=r['path']

    new_env['CK_PATH_TO_MLPERF_SCRIPT']=p

    # Generate user.conf from CMD if needed for reproducibility
    x=env.get('LOADGEN_GENERATE_USER_CONF','')
    if x!='':
       lines=x.strip().split(';')
       s='\n'.join(lines)

       r=ck.save_text_file({'text_file':'user-generated.conf', 'string':s})
       if r['return']>0: return r

    return {'return':0, 'new_env':new_env}

# Do not add anything here!
