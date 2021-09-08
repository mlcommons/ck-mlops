#
# Collective Knowledge (MLPerf benchmark system (SUT))
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, http://fursin.net
#

cfg = {}  # Will be updated by CK (meta description of this module)
work = {}  # Will be updated by CK (temporal data)
ck = None  # Will be updated by CK (initialized CK kernel)

# Local settings

#import sys
#import os
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#from ck_4edfa6cce73e7297 import ...

##############################################################################
# Initialize module

import os

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return': 0}

##############################################################################
# add MLPerf system

def add(i):
    """
    Input:  {
              (data_uoa) [str] - name of the CK entry for the bench.mlperf.system 
                                 (UID will be generated if empty)
              (repo_uoa) [str] - target CK repository
              (base) [str] - UOA of the bench.mlperf.system entry to be used as a base

              (dict) [dict] - system meta
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    duoa=i.get('data_uoa','')
    ruoa=i.get('repo_uoa','')

    base=i.get('base','')

    d=i.get('dict',{})

    # Attempt to load base
    if base!='':
       dtmp=d

       r=ck.access({'action':'load',
                    'module_uoa':work['self_module_uid'],
                    'data_uoa':base,
                    'repo_uoa':ruoa})
       if r['return']>0: return r
       d=r['dict']

       ck.merge_dicts({'dict1':d, 'dict2':dtmp})

    dd=d.get('desc',{})

    # Update keys if needed
    division=i.get('division','')
    if division=='':
       division=os.environ.get('CK_MLPERF_INFERENCE_DIVISION','')
       if division=='':
          division=ck.cfg.get('mlperf_inference_division','')

    if division!='':
       if division not in ['open','closed']:
          return {'return':1, 'error':'--division must be "open" or "closed"'}

       dd['division']=division

    # Check submitter
    submitter=i.get('submitter','')
    if submitter=='':
       submitter=os.environ.get('CK_MLPERF_SUBMITTER','')
       if submitter=='':
          submitter=ck.cfg.get('mlperf_submitter','')

    if submitter!='':
       dd['submitter']=submitter


    # Add extras
    ck.out('Detecting system info using CK automation recipes ...')
#    ck.out('')
    rd=ck.access({'action':'detect',
                  'module_uoa':cfg['module_deps']['platform'],
                  'out':''})

    if rd['return']>0: return rd

    ft=rd['features']

    x=ft.get('os',{}).get('name','')
    if x!='': 
       x1=ft.get('os',{}).get('name_long','')
       if x1!='': x+=' ('+x1+')'
       dd['operating_system']=x

    x=ft.get('cpu',{}).get('name','')
    if x!='': dd['host_processor_model_name']=x

    x=ft.get('cpu',{}).get('num_proc','')
    if x!='': dd['host_processor_core_count']=x

    x=ft.get('platform',{}).get('name','')
    if x!='': dd['system_name']=x

    sw_notes=dd.get('sw_notes','')
    other_software_stack=dd.get('other_software_stack','')
    if 'Collective Knowledge' in sw_notes:
       # Created by CK - rebuild it
      sw_notes=''
      other_software_stack=''

    r=ck.access({'action':'version'})
    if r['return']>0: return r

    ck_ver=r['version_str']
    sw_notes+='Powered by CK v'+ck_ver+' (https://github.com/ctuning/ck)'
    dd['sw_notes']=sw_notes

    # Check env
    renv=ck.access({'action':'show',
                    'module_uoa':'env'})
    if renv['return']>0: return renv

    lst=renv['lst']

    check_env={'CK_ENV_COMPILER_PYTHON':{'name':'Python'}, 
               'CK_ENV_COMPILER_GCC':{'name':'GCC'}}

    for l in lst:
        cus=l['meta'].get('customize',{})
        env=cus.get('env_prefix','')
        if env in check_env.keys():
           xver=cus.get('version','')
           if xver!='':
              if other_software_stack!='': other_software_stack+='; '
              other_software_stack+=check_env[env]['name']+' '+xver

    dd['other_software_stack']=other_software_stack

    # Create/update entry
    d['desc']=dd

    r=ck.access({'action':'update',
                 'module_uoa':work['self_module_uid'],
                 'data_uoa':duoa,
                 'repo_uoa':ruoa,
                 'dict':d,
                 'sort_keys':'yes',
                 'ignore_update':'yes',
                 'common':'yes'})
    if r['return']>0: return r

    p=r['path']

    # Record output of CK detect platform recipe
    p_output=os.path.join(p, 'ck-detect-platform-output.json')
    rx=ck.save_json_to_file({'json_file':p_output, 'dict':rd, 'sort_keys':'yes'})
    if rx['return']>0: return rx

    # Record output of CK show env
    p_env=os.path.join(p, 'ck-show-env.json')
    rx=ck.save_json_to_file({'json_file':p_env, 'dict':renv, 'sort_keys':'yes'})
    if rx['return']>0: return rx

    ck.out('')
    ck.out('Successfully created/updated MLPerf system in CK: {}'.format(r['data_uoa']))
    ck.out('  (Output from "ck detect platform": {})'.format(p_output))
    ck.out('  (Output from "ck show env": {})'.format(p_env))
    ck.out('')
    ck.out('Please, update the following file with system meta description manually:')
    ck.out('  '+os.path.join(p, '.cm', 'meta.json'))

    return r
