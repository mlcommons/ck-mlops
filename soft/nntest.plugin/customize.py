#
# Copyright (c) 2020 cTuning foundation.
# See CK COPYRIGHT.txt for copyright details.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Collective Knowledge (individual environment - setup)
#
# Developer: Gavin Simpson gavin.s.simpson@gmail.com
#

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

    iv=i.get('interactive','')

    env=i.get('env',{})
    cfg=i.get('cfg',{})
    deps=i.get('deps',{})
    tags=i.get('tags',[])
    cus=i.get('customize',{})

    envp=cus.get('env_prefix','')
    pi=cus.get('path_install','')

    host_d=i.get('host_os_dict',{})
    sdirs=host_d.get('dir_sep','')

    fp=cus.get('full_path','')
    if fp!='':
       p1=os.path.dirname(fp)
       pi=os.path.dirname(p1)

       cus['path_include']=pi+sdirs+'include'

    ep=cus.get('env_prefix','')
    if pi!='' and ep!='':
       env[ep]=pi

    install_env = cus.get('install_env', {})

    # Just copy those without any change in the name:
    for varname in install_env.keys():
        if varname.startswith('PLUGIN_LSTM_'):
            env[varname] = install_env[varname]

    custom_path_name = ep + '_' + install_env['PLUGIN_SIGNATURE']
    env[custom_path_name] = pi

    python_path = os.path.join(pi, 'plugin')
    env['PYTHONPATH'] = python_path + ':${PYTHONPATH}'

    return {'return':0, 'bat': ''}
