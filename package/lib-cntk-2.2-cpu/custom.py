#
# CK configuration script for CNTK package
#
# Developer(s): 
#  * Grigori Fursin, dividiti/cTuning foundation
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
              (install-env) - prepare environment to be used before the install script
            }

    """

    # Get variables
    ck=i['ck_kernel']
    s=''

    hos=i['host_os_uoa']
    tos=i['target_os_uoa']

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    hbits=hosd.get('bits','')
    tbits=tosd.get('bits','')

    hname=hosd.get('ck_name','')    # win, linux
    hname2=hosd.get('ck_name2','')  # win, mingw, linux, android
    macos=hosd.get('macos','')      # yes/no

    # Check platform
    hplat=hosd.get('ck_name','')

    hproc=hosd.get('processor','')
    tproc=tosd.get('processor','')

    phosd=hosd.get('ck_name','')

    svarb=hosd.get('env_var_start','')
    svarb1=hosd.get('env_var_extra1','')
    svare=hosd.get('env_var_stop','')
    svare1=hosd.get('env_var_extra2','')

    iv=i.get('interactive','')
    cus=i.get('customize',{})
    ie=cus.get('install_env',{})
    cfg=i.get('cfg',{})
    deps=i.get('deps',{})
    ft=i.get('features',{})

    nie={}

    # Check bits
    if hbits!='64':
       return {'return':1, 'error':'only 64-bit host is supported for this package'}

    # Check python path and version
    python_ver=deps.get('python',{}).get('ver','')
    spython_ver=deps.get('python',{}).get('dict',{}).get('setup',{}).get('version_split',[])

    if len(spython_ver)<2:
       return {'return':1, 'error':'Python version is not recognized'}

    ver1=spython_ver[0]
    ver2=spython_ver[1]

    if not ((ver1==2 and ver2==7) or 
            (ver1==3 and ver2==4) or 
            (ver1==3 and ver2==5) or 
            (ver1==3 and ver2==6)):
       return {'return':1, 'error':'Python version is not supported'}

    ver=str(ver1)+str(ver2)
    f='cp'+ver+'-cp'+ver+'m'

    # Binary file
    pv=ie.get('CNTK_PACKAGE_VER','')
    fb='CNTK-'+pv.replace('.','-')

    # Various customizations
    if hname=='win':
       f+='-win_amd64'
       fb+='-Windows'
    else:
       if ver1==2 and ver2==7: f+='u'
       f+='-linux_x86_64'
       fb+='-Linux'

    f+='.whl'

    fb+='-64bit-'+ie.get('CNTK_PACKAGE_TYPE','')
    if hname=='win':
       fb2=fb+'.zip'
    else:
       fb+='.tar'
       fb2=fb+'.gz'

    nie['CNTK_PACKAGE_FILE_EXT']=f
    nie['CNTK_PACKAGE_BINARY_ARC']=fb2
    nie['CNTK_PACKAGE_BINARY_ARC2']=fb

    return {'return':0, 'install_env':nie}
