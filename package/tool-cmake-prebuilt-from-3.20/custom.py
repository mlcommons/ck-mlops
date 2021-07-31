#!/usr/bin/python

#
# Developers: 
#  - Grigori Fursin, OctoML
#

import os
import sys
import json

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

    cus=i['customize']
    ie=cus.get('install_env',{})
    nie={} # new env

    version=ie['CMAKE_VERSION']

    # Specializing downloads
    if macos=='yes':
       if hbits!='64':
          return {'return':1, 'error':'this package doesn\'t support non 64-bit MacOS'}

       name='cmake-'+version+'-macos-universal'

       nie['PACKAGE_NAME']=name+'.tar.gz'
       nie['PACKAGE_NAME1']=name+'.tar'

       nie['PACKAGE_UNGZIP']='YES'
       nie['PACKAGE_UNTAR']='YES'

    elif hname=='win':
       name='cmake-'+version+'-windows-'
       if hbits=='64':
          name+='x86_64'
       else:
          name+='i386'

       nie['PACKAGE_NAME']=name+'.zip'

       nie['PACKAGE_WGET_EXTRA']=ie['PACKAGE_WGET_EXTRA']+' -O '+name+'.zip'
       nie['PACKAGE_UNZIP']='YES'

    else:
       name='cmake-'+version+'-linux-'
       if habi.startswith('arm') or habi.startswith('aarch'):
          if hbits=='64':
             name+='aarch64'
          else:
             return {'return':1, 'error':'this package doesn\'t support armv7'}
       else:
          name+='x86_64'

       nie['PACKAGE_NAME']=name+'.tar.gz'
       nie['PACKAGE_NAME1']=name+'.tar'

       nie['PACKAGE_UNGZIP']='YES'
       nie['PACKAGE_UNTAR']='YES'


    # Unify output directory to prebuilt
    nie['PACKAGE_RENAME_DIR']='YES'
    nie['PACKAGE_RENAME_DIR1']=name
    nie['PACKAGE_RENAME_DIR2']='prebuilt'

    return {'return':0, 'install_env':nie}
