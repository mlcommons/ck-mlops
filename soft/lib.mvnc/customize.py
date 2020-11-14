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
# parse software version

def version_cmd(i):

    ck=i['ck_kernel']
    fp=i['full_path']

    # Read file with version
    print (fp)
    p1=os.path.dirname(fp)
    px=os.path.join(p1,'version.txt')

    r=ck.load_text_file({'text_file':px})
    if r['return']>0: return r
    ver=r['string'].strip()

    return {'return':0, 'version':ver}

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

    p1=os.path.dirname(fp)
    pi=os.path.dirname(p1)

    env[ep]=pi
    env[ep+'_NCSDK']=p1

    px=os.path.join(pi,'caffe')
    py=''
    if os.path.isdir(px):
       env[ep+'_CAFFE']=px

       py=os.path.join(px,'python')
       if os.path.isdir(py):
          env[ep+'_CAFFE_PYTHON']=py

    if py!='':
       if winh=='yes':
           s+='\nset PYTHONPATH=%PYTHONPATH%;'+py+'\n'
       else:
           s+='\nexport PYTHONPATH=${PYTHONPATH}:'+py+'\n'
       s+='\n'

    src_path=cus.get('src_path','')
    if src_path!='' and os.path.isdir(src_path):
       env[ep+'_SRC']=src_path

    return {'return':0, 'bat':s}
