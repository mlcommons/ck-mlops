#
# Collective Knowledge (MLPerf inference benchmark automation)
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
import os
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#from ck_8b543d3874cdfdb0 import ...

##############################################################################
# Initialize module



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
# import results

def ximport(i):
    """
    Input:  {
              (target_repo) - where to record
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    target_repo=i.get('target_repo','')

    # Query envs with MLPerf inference results
    r=ck.access({'action':'search',
                 'module_uoa':cfg['module_deps']['env'],
                 'add_meta':'yes',
                 'tags':'mlperf,inference,results'})
    if r['return']>0: return r

    lst=r['lst']

    if len(lst)==0:
       return {'return':1, 'error':'install CK package with MLPerf results'}

    submitters=[]

    for l in lst:
        p=l['path']
        m=l['meta']

        cus=m.get('customize',{})
        ie=cus.get('install_env',{})

        ver=ie.get("PACKAGE_VERSION",'')

        ck.out('************************************************************')
        ck.out('MLPerf inference results: '+ver)

        path_results=m.get('env',{}).get('CK_ENV_MLPERF_INFERENCE_RESULTS','')
        ck.out('Path results: '+path_results)

        divisions=cfg['divisions']

        for division in divisions:
            ck.out('  Division: '+division)

            p=os.path.join(path_results, division)

            submitter_list=os.listdir(p)

            for submitter in submitter_list:
                if submitter.startswith('.'):
                   continue

                ck.out('    Submitter: '+submitter)

                # Check if exists
                dd={}

                ii={'action':'load',
                    'module_uoa':cfg['module_deps']['bench.mlperf.submitter'],
                    'data_uoa':submitter}
                r=ck.access(ii)
                if r['return']==0:
                   # Update meta
                   dd=r['dict']
                   ii['action']='update'
                   ii['ignore_update']='yes'
                else:
                   if r['return']==16:
                      ii['action']='add'

                # Add versions
                miv=dd.get('mlperf_inference_versions',[])
                if ver not in miv:
                   miv.append(ver)
                dd['mlperf_inference_versions']=miv

                ii['repo_uoa']=target_repo
                ii['dict']=dd
                ii['sort_keys']='yes'

                # Add/update submitter
                r=ck.access(ii)
                if r['return']>0: return r

                p_submitter=os.path.join(p, submitter)

                p_systems=os.path.join(p_submitter, 'systems')

                # Sometimes directory is empty - skip
                if not os.path.isdir(p_systems):
                   ck.out('      WARNING: no systems found!')
                   continue

                r=get_systems({'submitter':submitter,
                               'path':p_systems,
                               'target_repo':target_repo})
                if r['return']>0: return r

                # systems with dict 
                d_systems=r['d_systems']

                # Go through systems
                ck.out('')
                ck.out('      *** Searching for measurements and results ***')
                for system in d_systems:
                    ck.out('         '+system)

                    # Results may not be there (added system but didn't submit results)
                    p_results=os.path.join(p_submitter, 'results', system)

                    if not os.path.isdir(p_results):
                       ck.out('           WARNING: results not found')
                       continue

                    # List ML models
                    models=os.listdir(p_results)

                    for informal_model in models:
                        p_model=os.path.join(p_results, informal_model)
                        if not os.path.isdir(p_model):
                           continue

                        ck.out('            Informal ML model name: '+informal_model)

                        # List scenarios
                        for scenario in cfg['scenarios']:
                            p_scenario=os.path.join(p_model, scenario)
                            if os.path.isdir(p_scenario):
                               ck.out('              Scenario: '+scenario)

                               # Checking performance (first run only - other runs are not needed from v1.0)
                               pp=os.path.join(p_scenario, 'performance', 'run_1')
                               if not os.path.isdir(pp):
                                  ck.out('               WARNING: no performance results')
                                  continue

                               r=get_performance({'path':pp})
                               if r['return']>0: return r

                               # Reading accuracy

                               # Reading power


                               # Check associated measurements
                               p_measurements=os.path.join(p_submitter, 'measurements', system, informal_model, scenario)

                               if not os.path.isdir(p_measurements):
                                  ck.out('xyz1')




    return {'return':0}

def get_performance(i):
    path=i['path']

    filename=os.path.join(path, 'mlperf_log_summary.txt')

    r=ck.load_text_file({'text_file':filename, 'split':'yes'})
    if r['return']>0: return r
    print (r)
    input('xyz')


    return {'return':0}

def get_systems(i):
    submitter=i['submitter']
    p=i['path']
    target_repo=i['target_repo']

    systems=os.listdir(p)

    d_systems={}

    for system in systems:
        if system.endswith('.json'):

           system_name=system[:-5]

           ck.out('      System: '+system_name)

           # Load this file
           ps=os.path.join(p, system)

           r=ck.load_json_file({'json_file':ps})
           if r['return']>0: return r

           ds=r['dict']

           d_systems[system_name]=ds

           # Add system (should be unique and global)
           ii={'action':'load',
               'module_uoa':cfg['module_deps']['bench.mlperf.system'],
               'data_uoa':system_name,
               'repo_uoa':target_repo}
           r=ck.access(ii)
           if r['return']>0 and r['return']!=16: return r

           if r['return']==0:
              ck.out('                 ALREADY EXISTS')
              continue

           ii['action']='add'
           ii['dict']={'desc':ds}
           ii['sort_keys']='yes'
           ii['ignore_update']='yes'
           r=ck.access(ii)
           if r['return']>0: return r

    return {'return':0, 'd_systems':d_systems}
