#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Gavin Simpson
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

    ck              = i['ck_kernel']
    cus             = i.get('customize',{})
    full_path       = cus.get('full_path','')
    env             = i['env']
    install_root    = os.path.dirname(full_path)
    install_env     = cus.get('install_env', {})
    env_prefix      = cus['env_prefix']
    val_map         = install_env['CK_CALIBRATION_VAL_MAP_FILE']

    env[env_prefix + '_ROOT'] = install_root
    env[env_prefix + '_VAL_MAP_PATH'] = os.path.join(install_root, val_map)

    return {'return':0, 'bat':''}
