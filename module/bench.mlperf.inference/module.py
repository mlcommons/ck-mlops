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

import re

#import sys
import os
#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#from ck_8b543d3874cdfdb0 import ...

line='************************************************************'

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
              (target_repo) - repo where to record
              (target_data) - data where to record
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    target_repo=i.get('target_repo','')
    target_data=i.get('target_data','')

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

    ck_submitters=[]

    for l in lst:
        p=l['path']
        m=l['meta']

        cus=m.get('customize',{})
        ie=cus.get('install_env',{})

        ver=ie.get("PACKAGE_VERSION",'')

        ck.out(line)
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

                    raw_meta_system=d_systems[system]

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
                        for scenario in os.listdir(p_model):
                            lscenario=scenario.lower()
                            if lscenario not in cfg['scenarios']:
                               continue

                            p_scenario=os.path.join(p_model, scenario)
                            if os.path.isdir(p_scenario):
                               ck.out('              Scenario: '+lscenario)

                               # Checking performance (first run only - other runs are not needed from v1.0)
                               pp=os.path.join(p_scenario, 'performance', 'run_1')
                               if not os.path.isdir(pp):
                                  ck.out('               WARNING: no performance results')
                                  continue

                               r=get_performance({'path':pp,
                                                  'scenario_dir':lscenario})
                               if r['return']>0: return r

                               raw_meta_perf=r['raw_meta']
                               meta_perf=r['meta']

                               # Reading accuracy
                               pa=os.path.join(p_scenario, 'accuracy')
                               if not os.path.isdir(pa):
                                  ck.out('               WARNING: no accuracy results')
                                  continue

                               r=get_accuracy({'path':pa,
                                               'scenario_dir':lscenario})
                               if r['return']>0: return r

                               raw_meta_acc=r['raw_meta']
                               meta_acc=r['meta']

                               # Reading power
                               pr=os.path.join(p_scenario, 'performance', 'power')
                               found_power=False
                               if os.path.isdir(pr):
                                  r=get_power({'path_power':pr,
                                               'path_perf':pp,
                                               'scenario_dir':lscenario})
                                  if r['return']>0: return r

                                  raw_meta_power=r['raw_meta']
                                  meta_power=r['meta']

                                  found_power=True

                               # Check associated measurements
                               p_measurements=os.path.join(p_submitter, 'measurements', system, informal_model, scenario)

                               if not os.path.isdir(p_measurements):
                                  ck.out('               WARNING: no measurement directory: '+p_measurements)
                                  continue

                               r=get_measurement({'path':p_measurements})
                               if r['return']>0: return r

                               raw_meta_measurements=r['raw_meta']
                               meta_measurements=r['meta']

                               if meta_measurements.get('problem', False)==True:
                                  ck.out('               WARNING: problem with measurement directory: '+p_measurements+' ('+meta_measurements['problem_str']+')')
                                  continue

                               # Merging all meta
                               result={}

                               result.update(raw_meta_system)

                               result.update(raw_meta_perf)
                               result.update(meta_perf)

                               result.update(raw_meta_acc)
                               result.update(meta_acc)

                               if found_power:
                                  result.update(raw_meta_power)
                                  result.update(meta_power)

                               result.update(raw_meta_measurements)
                               result.update(meta_measurements)

                               result['mlperf_version']=ver

                               # Convert to int/float
                               for k in result:
                                   value=result[k]

                                   try:
                                      if '.' in value:
                                         value = float(value)
                                      else:
                                         if value=='true' or value=='false':
                                            value = bool(value)
                                         else:
                                            value = int(value)
                                   except Exception as e:
                                      pass

                                   result[k]=value

                               # Add extras / calculate ratios
                               # Check notes
                               ck_used=False
                               notes=result.get('sw_notes','').lower()
                               if 'collective knowledge' in notes or ' ck ' in notes or submitter.lower() in ['octoml','dividiti','krai']:
                                  ck_used=True
                                  if submitter=='Dividiti': submitter='dividiti'
                                  if submitter not in ck_submitters:
                                     ck_submitters.append(submitter)
                               result['ck_used']=ck_used

                               # Recording results
                               task=result.get('task','').replace(' ','-').lower()
                               system_type=result.get('system_type','datacenter') # old format (v0.5) - datacenter

                               if task!='' and system_type!='':
                                  if target_data!='':
                                     duoa=target_data
                                  else:
                                     duoa='mlperf-inference-all-'+task+'-'+system_type+'-'+lscenario

                                  tags='bench,mlperf,inference,mlperf-inference,all,'+task+','+system_type+','+lscenario

                                  ii={'action':'push',
                                      'module_uoa':cfg['module_deps']['result'],
                                      'dict':result,
                                      'user':submitter,
                                      'repo_uoa':target_repo,
                                      'data_uoa':duoa,
                                      'tags':tags}
                                  r=ck.access(ii)
                                  if r['return']>0: return r

#    ck.out(line)
#    ck.out('CK automation was used by:')
#    for cks in ck_submitters:
#        ck.out(' * '+cks)

    return {'return':0}

##############################################################################
def get_measurement(i):
    path=i['path']

    raw_meta={}
    meta={}

    json_files=[]
    for f in os.listdir(path):
        if f.endswith('.json') and f!='config.json':
           json_files.append(os.path.join(path,f))

    if len(json_files)==0 or len(json_files)>1:
       # Very rare case
       meta['problem']=True
       meta['problem_str']='either couldn\'t find measurements files or found more than 1'
    else:
       # Load json file
       r=ck.load_json_file({'json_file':json_files[0]})
       if r['return']>0: return r

       raw_meta=r['dict']
       meta=raw_meta

    return {'return':0, 'raw_meta':raw_meta, 'meta':meta}

##############################################################################
def get_power(i):
    # Based on parser from submission-checker.py

    import datetime
    import json

    path_power=i['path_power']
    path_perf=i['path_perf']

    scenario_dir=i.get('scenario_dir','')

    datetime_format = '%m-%d-%Y %H:%M:%S.%f'

    raw_meta={}
    meta={}

    p1=os.path.join(path_power, 'server.json')
    r=ck.load_json_file({'json_file':p1})
    if r['return']>0: return r

    server_timezone=datetime.timedelta(seconds=r['dict']["timezone"])

    p2=os.path.join(path_power, 'client.json')
    r=ck.load_json_file({'json_file':p2})
    if r['return']>0: return r

    client_timezone=datetime.timedelta(seconds=r['dict']["timezone"])

    # Log
    p3=os.path.join(path_perf, 'mlperf_log_detail.txt')

    r=ck.load_text_file({'text_file':p3, 'split_to_list':'yes'})
    if r['return']>0: return r

    lst=r['lst']

    mlperf_log={}

    for l in lst:
        j1=l.find('{')
        if j1>=0:
           j2=l.rfind('}')
           x=l[j1:j2+1]
           y=json.loads(x)

        mlperf_log[y['key']]=y['value']

    power_begin = datetime.datetime.strptime(mlperf_log["power_begin"], datetime_format) + client_timezone
    power_end = datetime.datetime.strptime(mlperf_log["power_end"], datetime_format) + client_timezone

    # Check spl.txt
    p4=os.path.join(path_perf, 'spl.txt')

    r=ck.load_text_file({'text_file':p4, 'split_to_list':'yes'})
    if r['return']>0: return r

    lst=r['lst']

    # Similar to parser from submission-checker.py
    power_list=[]
    for l in lst:
        if l!='':
           timestamp = datetime.datetime.strptime(l.split(",")[1], datetime_format)+server_timezone
           if timestamp>power_begin and timestamp<power_end:
              power_list.append(float(l.split(",")[3]))

    avg_power = sum(power_list) / len(power_list)
    if scenario_dir in ["offline", "server"]:
        meta['characteristics.power']=avg_power
    elif scenario_dir in ['multistream']:
        power_duration = (power_end - power_begin).total_seconds()
        num_samples = mlperf_log["generated_query_count"] * mlperf_log["generated_samples_per_query"]
        meta['characteristics.power'] = avg_power * power_duration / num_samples
    elif scenario_dir in ["singlestream"]:
        power_duration = (power_end - power_begin).total_seconds()
        num_samples = mlperf_log["result_qps_with_loadgen_overhead"] * power_duration
        meta['characteristics.power'] = avg_power * power_duration / num_samples

    return {'return':0, 'raw_meta':raw_meta, 'meta':meta}

##############################################################################
def get_accuracy(i):
    path=i['path']
    scenario_dir=i.get('scenario_dir','')

    raw_meta={}
    meta={}

    filename=os.path.join(path, 'accuracy.txt')

    if not os.path.isfile(filename):
       meta['problem']=True
       meta['problem_str']='accuracy.txt not found'
       ck.out('               WARNING: '+meta['problem_str'])
       return {'return':0, 'raw_meta':raw_meta, 'meta':meta}

    r=ck.load_text_file({'text_file':filename, 'split_to_list':'yes'})
    if r['return']>0: return r

    lst=r['lst']

    # Attempt to automatically detect the type of accuracy
    found=False
    for l in lst:
        if 'accuracy' in l and 'good' in l and 'total' in l:
           # image classification
           meta['task']='image classification'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==3:
              meta['characteristics.accuracy']=numbers[0]
              meta['characteristics.good']=numbers[1]
              meta['characteristics.total']=numbers[2]

           found=True
           break

        elif 'BLEU: ' in l:
           # NMT: Neural Machine Translation System
           meta['task']='NMT'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==1:
              meta['characteristics.blue']=numbers[0]

           found=True
           break

        elif 'mAP=' in l:
           # object detection
           meta['task']='object detection'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==1:
              meta['characteristics.mAP']=numbers[0]

           found=True
           break

        elif 'exact_match' in l and 'f1' in l:
           # NLP: Natural Language Processing
           meta['task']='NLP'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==2:
              meta['characteristics.exact_match']=numbers[0]
              meta['characteristics.f1']=numbers[1]

           found=True
           break

        elif 'mean' in l and 'whole tumor' in l and 'tumor core' in l and 'enhancing tumor' in l:
           # image segmentation
           meta['task']='image segmentation'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==4:
              meta['characteristics.mean']=numbers[0]
              meta['characteristics.whole tumor']=numbers[1]
              meta['characteristics.tumor core']=numbers[2]
              meta['characteristics.enhancing tumor']=numbers[3]

           found=True
           break

        elif 'Word Error Rate:' in l and 'accuracy' in l:
           meta['task']='speech recognition'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==2:
              meta['characteristics.word error rate']=numbers[0]
              meta['characteristics.accuracy']=numbers[1]

           found=True
           break

        elif 'AUC=' in l:
           meta['task']='recommendation'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==1:
              meta['characteristics.AUC']=numbers[0]

           found=True
           break

    if not found:
       meta['problem']=True
       meta['problem_str']='task not detected from accuracy.txt'
       ck.out('               WARNING: '+meta['problem_str'])

    return {'return':0, 'raw_meta':raw_meta, 'meta':meta}

##############################################################################
def get_performance(i):
    path=i['path']
    scenario_dir=i.get('scenario_dir','')

    filename=os.path.join(path, 'mlperf_log_summary.txt')

    r=ck.load_text_file({'text_file':filename, 'split_to_list':'yes'})
    if r['return']>0: return r

    lst=r['lst']

    # Basic parsing and splitting

    raw_meta={}
    meta={}

    for l in lst:
        if ':' in l:
           x=l.strip().split(':')
           if len(x)==2:
              key=x[0].strip()
              value=x[1].strip()

              raw_meta[key]=value

    # Fixing problems
    # Sometimes Scenario has space:
    scenario=raw_meta.get('Scenario','')
    scenario=scenario.replace(' ','').lower()

    # Unify meta depending on scenario
    problem=False
    if scenario=='':
       problem=True
       sproblem='scenario is empty in meta'
    elif scenario!=scenario_dir:
       problem=True
       sproblem='scenario in meta ({}) doesn\'t match directory ({})'.format(scenario, scenario_dir)

    # Report problem but continue processing based on the scenario in meta
    # Most of submissions dividiti, Krai and Edgecortix have issues:
    #  (offline scenario has a meta from singlestream)
    if scenario=='offline':
       v=raw_meta.get('Samples per second', None)
       if v==None:
          problem=True
          sproblem='characteristic is not found'

       meta['characteristics.samples_per_second']=v
    elif scenario=='server':
       v=raw_meta.get('Scheduled samples per second', None)
       if v==None:
          problem=True
          sproblem='characteristic is not found'

       meta['characteristics.scheduled_queries_per_second']=v
    elif scenario=='singlestream':
       v=raw_meta.get('90th percentile latency (ns)', None)
       if v==None:
          problem=True
          sproblem='characteristic is not found'

       v=float(v)
       meta['characteristics.90th_percentile_latency_ns']=v
       meta['characteristics.90th_percentile_latency_us']=v/1e3
       meta['characteristics.90th_percentile_latency_ms']=v/1e6
       meta['characteristics.90th_percentile_latency_s']=v/1e9
    elif scenario=='multistream':
       v=raw_meta.get('Samples per query', None)
       if v==None:
          problem=True
          sproblem='characteristic is not found'

       meta['characteristics.samples_per_query']=v

    meta['Scenario']=scenario
    meta['problem']=problem

    if problem:
       meta['problem_str']=sproblem
       ck.out('                               WARNING: '+sproblem)

    return {'return':0, 'raw_meta':raw_meta, 'meta':meta}

##############################################################################
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
