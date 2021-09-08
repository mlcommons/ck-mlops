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

    version=ie.get('BAZEL_VERSION','').strip()
    if version=='':
        return {'return':1, 'error':'internal problem - BAZEL_VERSION is not defined in env'}

    ck.out('')
    ck.out('Bazel version: '+version)
    ck.out('')

    # Update URL
    package_url=ie['PACKAGE_URL']
    package_url+='/'+version
    nie['PACKAGE_URL']=package_url

    # Update vars
    name='bazel-'+version+'-'

    if macos=='yes':
       if hbits!='64':
          return {'return':1, 'error':'this package doesn\'t support non 64-bit MacOS'}

       name+='installer-darwin-'

       if habi.startswith('arm') or habi.startswith('aarch'):
          name+='arm64.sh'
       else:
          name+='x86_64.sh'
    elif hname=='win':
       name+='windows-x86_64.zip'
    else:
       if hbits!='64':
          return {'return':1, 'error':'this package doesn\'t support non 64-bit MacOS'}

       name+='installer-linux-'

       if habi.startswith('arm') or habi.startswith('aarch'):
          return {'return':1, 'error':'TBD: this CK package doesn\'t support Arm'}
       else:
          name+='x86_64.sh'

    nie['PACKAGE_NAME']=name

    return {'return':0, 'install_env':nie}
