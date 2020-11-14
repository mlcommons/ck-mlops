#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, cTuning foundation/dividiti
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

    p1=os.path.dirname(fp)
    pl=os.path.dirname(p1)
    p2=os.path.dirname(pl)
#    pb=os.path.dirname(p2)

#    env[ep]=pb
    env[ep+'_PYTHON_LIB']=pl

    pll=os.path.join(pl,'cntk','libs')

    # Check CNTK binary installation
    pb=os.path.join(p2,'cntk','cntk')
    if winh!='yes':
       pb=os.path.join(pb,'bin')

    pbn='cntk'
    if winh=='yes':
       pbn+='.exe'

    pb2=os.path.join(pb, pbn)

    if os.path.isfile(pb2):
       env[ep+'_BIN']=pb
       env[ep+'_NAME']=pbn
       env[ep+'_FULL']=pb2

       pl1=os.path.join(p2, 'cntk', 'cntk', 'lib')
       pl2=os.path.join(p2, 'cntk', 'dependencies', 'lib')

       r = ck.access({'action': 'lib_path_export_script', 'module_uoa': 'os', 'host_os_dict': hosd, 'lib_path': pl1})
       if r['return']>0: return r
       s += r['script']

       r = ck.access({'action': 'lib_path_export_script', 'module_uoa': 'os', 'host_os_dict': hosd, 'lib_path': pl2})
       if r['return']>0: return r
       s += r['script']

       r = ck.access({'action': 'lib_path_export_script', 'module_uoa': 'os', 'host_os_dict': hosd, 'lib_path': pll})
       if r['return']>0: return r
       s += r['script']

    if winh=='yes':
        s+='\nset PYTHONPATH='+pl+';%PYTHONPATH%\n'
    else:
        s+='\nexport PYTHONPATH='+pl+':${PYTHONPATH}\n'

    for k in ienv:
        env[k]=ienv[k]


    return {'return':0, 'bat':s}
