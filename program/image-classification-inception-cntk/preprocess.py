#
# Preprocessing Caffe templates
#
# Developers:
# - Grigori Fursin, cTuning foundation, 2016
# - Anton Lokhmotov, dividiti, 2017
#

import json
import os
import re

def ck_preprocess(i):

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    env=i['env']
    nenv={} # new environment to be added to the run script

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']
    remote=tosd.get('remote','')

    b=''

    cur_dir=os.getcwd()

    script=env.get('CNTK_SCRIPT','')
    if script=='':
       return {'return':1, 'error':'CNTK_SCRIPT env variable is not defined in program meta'}

    ff=os.path.join('..','source','BrainScript',script)

    if not os.path.isfile(ff):
       return {'return':1, 'error':'Can\'t find BrainScipt file ('+ff+')'}

    # Read script
    r=ck.load_text_file({'text_file':ff})
    if r['return']>0: return r
    s=r['string']

    train_dir=deps['imagenet-train']['dict']['env']['CK_ENV_DATASET_IMAGENET_TRAIN']
    train_map=deps['imagenet-train-cntk']['dict']['env']['CK_ENV_DATASET_IMAGENET_TRAIN_CNTK_TRAIN_MAP_FULLNAME']
    val_map=deps['imagenet-train-cntk']['dict']['env']['CK_ENV_DATASET_IMAGENET_TRAIN_CNTK_VAL_MAP_FULLNAME']

    # Update script (replace some vars)

    s=s.replace('ConfigDir   = "$RootDir$"', 'ConfigDir   = "../source/BrainScript"')
    s=s.replace('DataDir     = "$RootDir$"', 'DataDir     = "'+train_dir+'"')
    s=s.replace('OutputDir   = "$RootDir$/Output"', 'OutputDir   = "./Output"')

    s=s.replace('"$DataDir$/train_map.txt"', '"'+train_map+'"')
    s=s.replace('"$DataDir$/val_map.txt"', '"'+val_map+'"')

    did=env.get('DEVICE_ID','')
    if did!='':
       s=s.replace('deviceId = "Auto"', 'deviceId = "'+did+'"')

    mb=env.get('BATCH_SIZE','')
    if mb=='': mb='256'

    s=s.replace('minibatchSize = 256 # 8 GPUs', 'minibatchSize = '+str(mb))

    # Record script
    tmp_script=env.get('CNTK_SCRIPT_TMP','')
    r=ck.save_text_file({'text_file':tmp_script, 'string':s})
    if r['return']>0: return r

    return {'return':0, 'bat':b, 'new_env':nenv}

# Do not add anything here!
