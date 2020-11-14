#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Author: Grigori Fursin, cTuning foundation/dividiti
#

import os

##############################################################################
# setup environment setup

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
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              bat          - prepared string for bat file
            }

    """

    import os

    # Get variables
    ck=i['ck_kernel']
    s=''

    iv=i.get('interactive','')

    cus=i.get('customize',{})
    fp=cus.get('full_path','')

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    winh=hosd.get('windows_base','')

    ienv=cus.get('install_env',{})

    env=i['env']
    ep=cus['env_prefix']

#    p1=os.path.dirname(fp)
    pl=os.path.dirname(fp)
    pi=os.path.dirname(pl)

    ptvm=os.path.join(pi,'python')
    ptopi=os.path.join(pi,'topi','python')

    env[ep]=pi
    env[ep+'_LIB']=pl
    env[ep+'_PYTHON_LIB']=ptvm
    env[ep+'_PYTHON_TOPI_LIB']=ptopi

    cus['path_lib']=pl

    r = ck.access({'action': 'lib_path_export_script', 
                   'module_uoa': 'os', 
                   'host_os_dict': hosd, 
                   'lib_path': cus.get('path_lib', '')})
    if r['return']>0: return r
    s += r['script']

    if winh=='yes':
        s+='\nset PYTHONPATH='+ptvm+';'+ptopi+';%PYTHONPATH%\n'
        s+='\nset TVM_PATH='+pi+'\n'
    else:
        s+='\nexport PYTHONPATH='+ptvm+':'+ptopi+':${PYTHONPATH}\n'
        s+='\nexport TVM_PATH='+pi+'\n'

    for k in ienv:
        if k.startswith('TVM_') or k=='CK_PYTHON_IPYTHON_BIN_FULL' or k=='CK_ENV_COMPILER_PYTHON_FILE':
           env[k]=ienv[k]

    return {'return':0, 'bat':s}
