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

                

    return {'return':0}
