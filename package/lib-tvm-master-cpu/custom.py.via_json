#!/usr/bin/python

#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os
import sys
import json

##############################################################################
def pre_path(i):
    tags=i['tags']
    env=i.get('install_env',{})

    # Add tags depending on env
    if env.get('USE_OPENCL','').lower()=='on' and 'vopencl' not in tags: tags.append('vopencl')
    if env.get('USE_CUDA','').lower()=='on' and 'vcuda' not in tags: tags.append('vcuda')

    return {'return':0}

##############################################################################
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

              (install_env) - prepare environment to be used before the install script
            }

    """

    import os
    import shutil

    # Get variables
    o=i.get('out','')

    ck=i['ck_kernel']

    hos=i['host_os_uoa']
    tos=i['target_os_uoa']

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    hbits=hosd.get('bits','')
    tbits=tosd.get('bits','')

    hname=hosd.get('ck_name','')    # win, linux
    hname2=hosd.get('ck_name2','')  # win, mingw, linux, android
    macos=hosd.get('macos','')      # yes/no

    hft=i.get('features',{}) # host platform features
    habi=hft.get('os',{}).get('abi','') # host ABI (only for ARM-based); if you want to get target ABI, use tosd ...
                                        # armv7l, etc...

    p=i['path']

    env=i['env']

    pi=i.get('install_path','')

    deps=i['deps']

    cus=i['customize']
    ie=cus.get('install_env',{})
    nie={} # new env

    rep={} # Prepare replacements

    # Check if LLVM is used and set CK_LLVM_CONFIG
    env1=deps.get('compiler',{}).get('dict',{}).get('env',{})
    p1=env1.get('CK_ENV_COMPILER_LLVM_BIN','')
    if p1=='':
       env1=deps.get('llvm-compiler',{}).get('dict',{}).get('env',{})
       p1=env1.get('CK_ENV_COMPILER_LLVM_BIN','')
    if p1!='':
       p2=env1['CK_LLVM_CONFIG']

       llvm_config=os.path.join(p1,p2)

       rep['USE_LLVM OFF']='USE_LLVM '+llvm_config

    # Check OpenCL
    if ie.get('USE_OPENCL','').lower()=='on':
       rep['USE_OPENCL OFF']='USE_OPENCL ON'

    # Check CUDA
    if ie.get('USE_CUDA','').lower()=='on':
       rep['USE_CUDA OFF']='USE_CUDA ON'

    # Generate tmp file
    r=ck.gen_tmp_file({})
    if r['return']>0: return r

    tmp_file_name=r['file_name']

    nie['TMP_TVM_CMAKE_UPDATE_FILE']=tmp_file_name

    # Save JSON to tmp file (will be picked up by install.sh and recored to INSTALL dir)
    r=ck.save_json_to_file({'json_file':tmp_file_name, 'dict':rep})
    if r['return']>0: return r

    return {'return':0, 'install_env':nie}
