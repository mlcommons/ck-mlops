#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Leo Gordon @ dividiti
#

import os


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


    # Get variables
    ck              = i['ck_kernel']
    cus             = i.get('customize',{})
    fp              = cus.get('full_path','')

    path_lib        = os.path.dirname( fp )
    install_root    = os.path.dirname( path_lib )
    path_include    = os.path.join( install_root, 'include' )

    env                         = i['env']
    hosd                        = i['host_os_dict']
    env_prefix                  = cus['env_prefix']

    # We need to pass this path to the users of ArmNN library
    #
    boost_include               = i.get('deps',{}).get('lib-boost',{}).get('dict',{}).get('customize',{}).get('path_include','')

    # This env-setting method is the most introspective (the paths generated may be post-processed),
    # but rather restrictive - only certain variable names are taken into account:
    # (higher level)
    #
    cus['path_lib']             = path_lib
    cus['path_include']         = path_include
    cus['path_includes']        = [boost_include, path_include]

    # Any variable that ends up in "env" will become a part of the env-setting script:
    # (medium level)
    #
    env[env_prefix]             = install_root

    # A monolythic OS-dependent script is generated here:
    # (lower level)
    #
    r = ck.access({'action': 'lib_path_export_script', 
                   'module_uoa': 'os', 
                   'host_os_dict': hosd, 
                   'lib_path': path_lib })
    if r['return']>0: return r
    shell_setup_script_contents = r['script']

    return {'return': 0, 'bat': shell_setup_script_contents}
