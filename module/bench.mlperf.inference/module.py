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

#from ck_8b543d3874cdfdb0 import multidimensional_pareto as mul_par

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

    cur_dir=os.getcwd()

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

    # Attempt to load meta from "result.cfg:mlperf.inference.all"
    result_cfg={}
    r=ck.access({'action':'load',
                 'module_uoa':'result.cfg',
                 'data_uoa':'mlperf.inference.all'})
    if r['return']==0:
       result_cfg=r['dict']

    # Hack
    for l in lst:
        p=l['path']
        m=l['meta']

        cus=m.get('customize',{})
        install_env=cus.get('install_env',{})
        package_url=install_env.get('PACKAGE_URL','')

        package_url_tree=package_url+'/tree/master'

        cus=m.get('customize',{})
        ie=cus.get('install_env',{})

        ver=ie.get("PACKAGE_VERSION",'')

        ck.out(line)
        ck.out('MLPerf inference results: '+ver)
        ck.out('Package URL: '+package_url)

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

                                   if k=='host_processor_core_count' and type(value)==str and value!='' and value!=None:
                                      # Process special cases like "4 (big); 4 (LITTLE)" (Arm)
                                      numbers=re.findall(r"[-+]?\d*\.\d+|\d+", value)

                                      value=0
                                      for n in numbers:
                                          value+=int(n)

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

                               # Add code/detail notes
                               note_details=package_url_tree+'/'+division+'/'+submitter+'/results/'+system
                               note_code=package_url_tree+'/'+division+'/'+submitter+'/code'

                               result['note_details']=note_details
                               result['note_code']=note_code

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

                               # Check cores and normalize
                               hp=result.get('host_processors_per_node','')
                               if hp!='' and hp!=None:
                                  hpc=result.get('host_processor_core_count','')
                                  if hpc!='' and hpc!=None:
                                     total_cores=hp*hpc
                                     result['total_cores']=total_cores

                               # Normalize per scenario for Processor vs Accelerator
                               use_accelerator=True
                               x=result.get('accelerator_model_name','')
                               y=result.get('accelerators_per_node','')
                               if x==None or x=='' or x=='-' or y==None or y=='' or y=='0' or y==0:
                                  use_accelerator=False
                               result['use_accelerator']=use_accelerator

                               normalize_processors=result.get('accelerators_per_node',1) if use_accelerator else result.get('host_processors_per_node',1)
                               normalize_cores=result.get('accelerators_per_node',1) if use_accelerator else result.get('total_cores',1)

                               result['normalize_processors']=normalize_processors
                               result['normalize_cores']=normalize_cores

                               power=result.get('characteristics.power',None)
                               if power!=None:
                                  result['characteristics.power.normalized_per_processor']=power/normalize_processors
                                  result['characteristics.power.normalized_per_core']=power/normalize_cores

                               if lscenario=="server":
                                  v=result.get('characteristics.scheduled_queries_per_second',None)
                                  if v!=None:
                                     result['characteristics.scheduled_queries_per_second.normalized_per_processor']=v/normalize_processors
                                     result['characteristics.scheduled_queries_per_second.normalized_per_core']=v/normalize_cores
                               elif lscenario=="offline":
                                  v=result.get('characteristics.samples_per_second',None)
                                  if v!=None:
                                     result['characteristics.samples_per_second.normalized_per_processor']=v/normalize_processors
                                     result['characteristics.samples_per_second.normalized_per_core']=v/normalize_cores
                               elif lscenario=="multistream":
                                  v=result.get('characteristics.samples_per_query',None)
                                  if v!=None:
                                     result['characteristics.samples_per_query.normalized_per_processor']=v/normalize_processors
                                     result['characteristics.samples_per_query.normalized_per_core']=v/normalize_cores


                               # Check dataset, modle and accuracy
                               system_type=result.get('system_type','datacenter') # old format (v0.5) - datacenter
                               task=result.get('task','').replace(' ','-').lower()
                               xtask=task.replace('-',' ')
                               result['task2']=xtask

                               if task=='' or system_type=='':
                                  continue

                               dataset=''
                               if task=='image-classification':
                                  dataset='ImageNet 2012'
                                  dataset_link='https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/datasets/imagenet2012.md'
                                  formal_model='resnet50-v1.5'
                                  formal_model_link='https://github.com/octoml/mlops/tree/main/package, https://github.com/ctuning/ai/tree/main/package'
                                  accuracy=99.0

                                  if ver=='v0.5' and 'mobilenet' in informal_model:
                                     formal_model='mobilenets-v1'

                               elif task=='object-detection':
                                  dataset_link='https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/datasets/coco2017.md'
                                  formal_model_link='https://github.com/octoml/mlops/tree/main/package, https://github.com/ctuning/ai/tree/main/package'

                                  dataset='COCO 2017 (1200x1200)'
                                  formal_model='ssd-resnet34'
                                  accuracy=99.0

                                  if system_type=='edge' or 'ssd' in informal_model or 'mobilenet' in informal_model:
                                     dataset='COCO 2017 (300x300)'
                                     formal_model='ssd-mobilenet'

                               elif task=='image-segmentation':
                                  dataset='BraTS 2019'
                                  dataset_link='https://www.med.upenn.edu/cbica/brats2019/data.html'
                                  formal_model_link=''
                                  formal_model='3d-unet'
                                  accuracy=99.9 if '99.9' in informal_model else 99.0

                               elif task=='speech-recognition':
                                  dataset='LibriSpeech'
                                  dataset_link=''
                                  formal_model_link=''
                                  formal_model='rnn-t'
                                  accuracy=99.0

                               elif task=='nlp':
                                  dataset='SQuAD v1.1'
                                  dataset_link=''
                                  formal_model_link=''
                                  formal_model='bert'
                                  accuracy=99.9 if '99.9' in informal_model else 99.0

                               elif task=='nmt':
                                  dataset='WMT E-G'
                                  dataset_link=''
                                  formal_model_link=''
                                  formal_model='nmt'
                                  accuracy=99.0

                               elif task=='recommendation':
                                  dataset='1TB Click Logs'
                                  dataset_link=''
                                  formal_model_link=''
                                  formal_model='dlrm'
                                  accuracy=99.9 if '99.9' in informal_model else 99.0

                               else:
                                  return {'return':1, 'error':'task ('+task+') is not recognized'}

                               result['dataset']=dataset
                               result['dataset_link']=dataset_link

                               result['formal_model']=formal_model
                               result['formal_model_link']=formal_model_link

                               result['formal_model_accuracy']=accuracy

                               result['informal_model']=informal_model
                               if division=='open':
                                  result['formal_model']=informal_model

                               # Link to submitter and system in CK
                               result['submitter_link']='https://github.com/ctuning/ck-mlperf-inference/tree/main/bench.mlperf.submitter/'+submitter
                               result['system_link']='https://github.com/ctuning/ck-mlperf-inference/tree/main/bench.mlperf.system/'+system
                               result['ck_system']=system

                               # Generate result UID
                               r=ck.gen_uid(i)
                               result['uid']=r['data_uid']

                               ###############################################################################
                               # Recording results-

                               if task!='' and system_type!='':
                                  if target_data!='':
                                     duoa=target_data
                                  else:
                                     duoa='mlperf-inference-all-'+task+'-'+system_type+'-'+lscenario

                                  tags='bench,mlperf,inference,mlperf-inference,all,'+task+','+system_type+','+lscenario

                                  # Create associated graph config
                                  fconfig='config-'+duoa+'-raw.json'

                                  dconfig={
                                    "data_config": {
                                      "dimensions": [
                                      ],
                                      "raw_config": {
                                        "tooltipValues": [
                                        ],
                                        "xVariationVisible": False,
                                        "yVariationVisible": False
                                      },
                                      "table_view": [
                                      ]
                                    }
                                  }

                                  dconfig['id']=duoa
                                  dconfig['tags']='mlperf-inference,all,'+task+','+system_type+','+lscenario+',raw'
                                  dconfig['name']='MLPerf&trade; inference benchmark; '+xtask+'; '+system_type+'; '+lscenario

                                  # Accuracy depending on a task
                                  if task=='image-classification':
                                     x1=('characteristics.accuracy', 'Accuracy (%)')
                                     tv=[{'key':x1[0], 'name':x1[1]}]
                                     dims=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]}]
                                     tt=[x1[0]]
                                     ydim=x1[0]
                                  elif task=='nmt':
                                     x1=('characteristics.blue', 'BLUE')
                                     tv=[{'key':x1[0], 'name':x1[1]}]
                                     dims=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]}]
                                     tt=[x1[0]]
                                     ydim=x1[0]
                                  elif task=='object-detection':
                                     x1=('characteristics.mAP', 'mAP (%)')
                                     tv=[{'key':x1[0], 'name':x1[1]}]
                                     dims=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]}]
                                     tt=[x1[0]]
                                     ydim=x1[0]
                                  elif task=='nlp':
                                     x1=('characteristics.exact_match', 'Exact Match')
                                     x2=('characteristics.f1', 'F1')
                                     tv=[{'key':x1[0], 'name':x1[1]},
                                         {'key':x2[0], 'name':x2[1]}]
                                     dims=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]},
                                           {'key':x2[0], 'name':x2[1], 'view_key':x2[0]}]
                                     tt=[x1[0],x2[0]]
                                     ydim=x1[0]
                                  elif task=='image-segmentation':
                                     x1=('characteristics.mean', 'Mean')
                                     x2=('characteristics.whole tumor', 'Whole Tumor')
                                     x3=('characteristics.tumor core', 'Tumor Core')
                                     x4=('characteristics.enhancing tumor', 'Enhancing Tumor')
                                     tv=[{'key':x1[0], 'name':x1[1]},
                                         {'key':x2[0], 'name':x2[1]},
                                         {'key':x3[0], 'name':x3[1]},
                                         {'key':x4[0], 'name':x4[1]}]
                                     dims=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]},
                                           {'key':x2[0], 'name':x2[1], 'view_key':x2[0]},
                                           {'key':x3[0], 'name':x3[1], 'view_key':x3[0]},
                                           {'key':x4[0], 'name':x4[1], 'view_key':x4[0]}]
                                     tt=[x1[0],x2[0],x3[0],x4[0]]
                                     ydim=x1[0]
                                  elif task=='speech-recognition':
                                     x1=('characteristics.accuracy', 'Accuracy (%)')
                                     x2=('characteristics.word error rate', 'Word Error Rate')
                                     tv=[{'key':x1[0], 'name':x1[1]},
                                         {'key':x2[0], 'name':x2[1]}]
                                     dims=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]},
                                           {'key':x2[0], 'name':x2[1], 'view_key':x2[0]}]
                                     tt=[x1[0],x2[0]]
                                     ydim=x1[0]
                                  elif task=='recommendation':
                                     x1=('characteristics.AUC', 'AUC')
                                     tv=[{'key':x1[0], 'name':x1[1]}]
                                     dims=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]}]
                                     tt=[x1[0]]
                                     ydim=x1[0]
                                  else:
                                     return {'return':1, 'error':'task ('+task+') is not recognized'}

                                  # Process other characteristics depending on scenario
                                  if lscenario=="singlestream":
                                     x1=('characteristics.90th_percentile_latency_ms', 'Latency (ms)')
                                     tv+=[{'key':x1[0], 'name':x1[1]}]
                                     dims+=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]}]
                                     tt+=[x1[0]]
                                     xdim=x1[0]
                                  elif lscenario=="server":
                                     x1=('characteristics.scheduled_queries_per_second', 'scheduled queries/second')
                                     x2=('characteristics.scheduled_queries_per_second.normalized_per_processor', 'scheduled queries/second/processor (experimental)')
                                     x3=('characteristics.scheduled_queries_per_second.normalized_per_core', 'scheduled queries/second/core (experimental)')
                                     tv+=[{'key':x1[0], 'name':x1[1]},
                                         {'key':x2[0], 'name':x2[1]},
                                         {'key':x3[0], 'name':x3[1]}]
                                     dims+=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]},
                                           {'key':x2[0], 'name':x2[1], 'view_key':x2[0]},
                                           {'key':x3[0], 'name':x3[1], 'view_key':x3[0]}]
                                     tt+=[x1[0],x2[0],x3[0]]
                                     xdim=x1[0]
                                  elif lscenario=="offline":
                                     x1=('characteristics.samples_per_second', 'samples/second')
                                     x2=('characteristics.samples_per_second.normalized_per_processor', 'samples/second/processor (experimental)')
                                     x3=('characteristics.samples_per_second.normalized_per_core', 'samples/second/core (experimental)')
                                     tv+=[{'key':x1[0], 'name':x1[1]},
                                         {'key':x2[0], 'name':x2[1]},
                                         {'key':x3[0], 'name':x3[1]}]
                                     dims+=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]},
                                           {'key':x2[0], 'name':x2[1], 'view_key':x2[0]},
                                           {'key':x3[0], 'name':x3[1], 'view_key':x3[0]}]
                                     tt+=[x1[0],x2[0],x3[0]]
                                     xdim=x1[0]
                                  elif lscenario=="multistream":
                                     x1=('characteristics.samples_per_query', 'samples/query')
                                     x2=('characteristics.samples_per_query.normalized_per_processor', 'samples/query/processor (experimental)')
                                     x3=('characteristics.samples_per_query.normalized_per_core', 'samples/query/core (experimental)')
                                     tv+=[{'key':x1[0], 'name':x1[1]},
                                         {'key':x2[0], 'name':x2[1]},
                                         {'key':x3[0], 'name':x3[1]}]
                                     dims+=[{'key':x1[0], 'name':x1[1], 'view_key':x1[0]},
                                           {'key':x2[0], 'name':x2[1], 'view_key':x2[0]},
                                           {'key':x3[0], 'name':x3[1], 'view_key':x3[0]}]
                                     tt+=[x1[0],x2[0],x3[0]]
                                     xdim=x1[0]

                                  result['dim_y_maximize']=True # Accuracy
                                  if task=='nlp':
                                     ydim=xdim
                                     xdim='seq_number'
                                     result['dim_y_maximize']=False

                                  dconfig['data_config']['raw_config']['xDimension']=xdim
                                  dconfig['data_config']['raw_config']['yDimension']=ydim

                                  # Finalize config
                                  dconfig['data_config']['dimensions']+=dims
                                  dconfig['data_config']['table_view']+=tv
                                  dconfig['data_config']['raw_config']['tooltipValues']+=tt

                                  ff=os.path.join(cur_dir, fconfig)
                                  r=ck.save_json_to_file({'json_file':fconfig, 'dict':dconfig, 'sort_keys':'yes'})
                                  if r['return']>0: return r

                                  # If CK v1.x used, prepare for Pareto to remove suboptimal points from raw DSE
                                  pareto=False
                                  if (task=='image-classification' or task=='object-detection') and lscenario=="singlestream":
                                     pareto=True

                                  if pareto:
                                     fconfig='config-'+duoa+'-pareto.json'

                                     dconfig['id']=duoa+'-pareto'
                                     dconfig['tags']='mlperf-inference,all,'+task+','+system_type+','+lscenario+',pareto'
                                     dconfig['name']='MLPerf&trade; inference benchmark; '+xtask+'; '+system_type+'; '+lscenario+' (Pareto per submitter)'

                                     ff=os.path.join(cur_dir, fconfig)
                                     r=ck.save_json_to_file({'json_file':fconfig, 'dict':dconfig, 'sort_keys':'yes'})
                                     if r['return']>0: return r

                                  result['dim_x_default']=xdim
                                  result['dim_y_default']=ydim

                                  # Next result

                                  ii={'action':'push',
                                      'module_uoa':cfg['module_deps']['result'],
                                      'dict':result,
                                      'user':submitter,
                                      'repo_uoa':target_repo,
                                      'data_uoa':duoa,
                                      'tags':tags+',raw'}
                                  r=ck.access(ii)
                                  if r['return']>0: return r

                                  dconfig['data_config']['default_key_x']=xdim
                                  dconfig['data_config']['default_key_y']=ydim
                                  dconfig['data_config']['default_sort_key']=xdim

                                  import copy
                                  tmp_result_cfg=copy.deepcopy(result_cfg)
                                  merge_dicts_and_append_lists({'dict1': tmp_result_cfg, 'dict2': dconfig})

                                  xmeta={
                                          "meta": {
                                            "info": " ",
                                            "scenario": "universal",
                                            "scenario_uid": "3bf7371412455a8f",
                                            "title": dconfig['name'],
                                            "viz_engine": "ck_beta"
                                          },
                                          "source": dconfig['name'],
                                          "tags": dconfig['tags'].split(',')
                                        }

                                  presult=r['path']
                                  pdesc=os.path.join(presult,'desc.json')
                                  r=ck.save_json_to_file({'json_file':pdesc, 'dict':tmp_result_cfg, 'sort_keys':'yes'})
                                  if r['return']>0: return r

                                  pdesc=os.path.join(presult,'meta.json')
                                  r=ck.save_json_to_file({'json_file':pdesc, 'dict':xmeta, 'sort_keys':'yes'})
                                  if r['return']>0: return r

                                  if pareto:
                                     ii['data_uoa']=duoa+'-pareto'
                                     ii['tags']=tags+',pareto'
                                     r=ck.access(ii)
                                     if r['return']>0: return r

                                     presult=r['path']
                                     pdesc=os.path.join(presult,'desc.json')
                                     r=ck.save_json_to_file({'json_file':pdesc, 'dict':tmp_result_cfg, 'sort_keys':'yes'})
                                     if r['return']>0: return r

                                     pdesc=os.path.join(presult,'meta.json')
                                     r=ck.save_json_to_file({'json_file':pdesc, 'dict':xmeta, 'sort_keys':'yes'})
                                     if r['return']>0: return r

#    ck.out(line)
#    ck.out('CK automation was used by:')
#    for cks in ck_submitters:
#        ck.out(' * '+cks)

    ruoa=target_repo if target_repo!='' else 'local'
    duoa=target_data if target_data!='' else 'mlperf-inference-*'

    # Finalizing archive

    ck.out(line)
    ck.out('Archiving results ...')

    p=os.path.join(cur_dir, 'ckr.zip')
    if os.path.isfile(p):
       ck.out('  Deleting old archive...')
       os.remove(p)

    r=ck.access({'action':'zip',
                 'out':'con',
                 'module_uoa':'repo',
                 'repo_uoa':ruoa,
                 'data':ruoa+':result:'+duoa})
    if r['return']>0: return r

    return {'return':0}

##############################################################################
# Merge intelligently dict1 with dict2 key by key in contrast with dict1.update(dict2)
#
# TARGET: end users

def merge_dicts_and_append_lists(i):
    """Merge intelligently dict1 with dict2 key by key in contrast with dict1.update(dict2)
       Target audience: end users

       It can merge sub-dictionaries and lists instead of substituting them

    Args:    
              dict1 (dict): merge this dict with dict2 (will be directly modified!)
              dict2 (dict): dict to be merged

    Returns:
              (dict): Unified CK dictionary:

                return (int): return code =  0, if successful
                                          >  0, if error
                (error) (str): error text if return > 0

                dict1 (dict): dict1 passed through the function

    """

    a = i['dict1']
    b = i['dict2']

    for k in b:
        v = b[k]
        if type(v) is dict:
            if k not in a:
                a.update({k: b[k]})
            elif type(a[k]) == dict:
                merge_dicts_and_append_lists({'dict1': a[k], 'dict2': b[k]})
            else:
                a[k] = b[k]
        elif type(v) is list:
            if k not in a:
               a[k] = []
            for y in v:
                a[k].append(y)
        else:
            a[k] = b[k]

    return {'return': 0, 'dict1': a}

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

        if 'AUC=' in l:
           meta['task']='recommendation'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==1:
              meta['characteristics.AUC']=numbers[0]
              meta['key.accuracy']='characteristics.AUC'

           found=True
           break

        elif 'BLEU: ' in l:
           # NMT: Neural Machine Translation System
           meta['task']='NMT'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==1:
              meta['characteristics.blue']=numbers[0]
              meta['key.accuracy']='characteristics.blue'

           found=True
           break

        elif 'mAP=' in l:
           # object detection
           meta['task']='object detection'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==1:
              meta['characteristics.mAP']=numbers[0]
              meta['key.accuracy']='characteristics.mAP'

           found=True
           break

        elif 'exact_match' in l and 'f1' in l:
           # NLP: Natural Language Processing
           meta['task']='NLP'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==2:
              meta['characteristics.exact_match']=numbers[0]
              meta['characteristics.f1']=numbers[1]
              meta['key.accuracy']='characteristics.f1'

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
              meta['key.accuracy']='characteristics.mean'

           found=True
           break

        elif 'Word Error Rate:' in l and 'accuracy' in l:
           meta['task']='speech recognition'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==2:
              meta['characteristics.word error rate']=numbers[0]
              meta['characteristics.accuracy']=numbers[1]
              meta['key.accuracy']='characteristics.accuracy'

           found=True
           break

        elif 'accuracy' in l and 'good' in l and 'total' in l:
           # image classification (must be at the end since has similar keys for AUC in v0.7
           meta['task']='image classification'

           numbers=re.findall(r"[-+]?\d*\.\d+|\d+", l)

           if len(numbers)==3:
              meta['characteristics.accuracy']=numbers[0]
              meta['characteristics.good']=numbers[1]
              meta['characteristics.total']=numbers[2]
              meta['key.accuracy']='characteristics.accuracy'

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

##############################################################################
# filter results (Pareto frontier)

def xfilter(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    duoa=i.get('data_uoa','mlperf-inference-*-pareto')
    tags=i.get('tags','pareto')

    r=ck.access({'action':'search',
                 'module_uoa':cfg['module_deps']['result'],
                 'data_uoa':duoa,
                 'tags':tags})
    if r['return']>0: return r

    lst=r['lst']

    for l in lst:
        ck.out(line)
        ck.out(l['data_uoa'])

        p=l['path']

        p1=os.path.join(p,'users')
        if not os.path.isdir(p1):
           continue

        for s in os.listdir(p1):
            # Raw (unprocessed) results from DSE come from 2 submitters mostly
            # Need to optimize based on our ACM REQUEST methodology
            if s.lower()!='dividiti' and s.lower()!='krai':
               continue

            p2=os.path.join(p1,s)
            if os.path.isdir(p2):
               results=[]
               ck.out('  '+p2)
               for res in os.listdir(p2):
                   if res.startswith('result-') and res.endswith('.json'):
                      pr=os.path.join(p2,res)
                      ck.out('  '+pr)

                      r=ck.load_json_file({'json_file':pr})
                      if r['return']>0: return r

                      d=r['dict']

                      results+=d

                      dim_x_default=results[0]['dim_x_default']
                      dim_y_default=results[0]['dim_y_default']
                      dim_y_maximize=results[0]['dim_y_maximize']

                      frontier_keys=[dim_x_default,dim_y_default]
                      reverse_keys=[]
                      if dim_y_maximize:
                         reverse_keys=[dim_y_default]

                      lresults=len(results)
                      ck.out('    Raw results: {}'.format(lresults))

                      r=ck.access({'action':'filter_2d',
                                   'module_uoa':cfg['module_deps']['math.frontier'],
                                   'points':results,
                                   'frontier_keys':frontier_keys,
                                   'reverse_keys':reverse_keys})
                      if r['return']>0: return r

                      frontier=r['frontier']

                      lpresults=len(frontier)
                      ck.out('    Results on Pareto: {}'.format(lpresults))

                      r=ck.save_json_to_file({'json_file':pr, 'dict':frontier})
                      if r['return']>0: return r

    return {'return':0}

##############################################################################
# run MLPerf inference benchmark

def run(i):
    """
    Input:  {
              (result_tag) [str] - extra tags to find environment with MLPerf inference results

              (version) [str] - MLPerf inference version (1.1 by default)

              (division) [str] - "closed" or "open"

              (framework) [str] - MLPerf framework
              (framework_ver) [str] -
              (framework_ext) [str] -

              (model) [str] - strict name if closed division and any name if open division

              (task) [str] -

              (workflow) [str] - force CK program workflow to run benchmark

              (scenario) [str] - usage scenario
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    result_tag=i.get('result_tag','')

    # Attempt to find/install package with MLPerf inference results
    tags='mlperf,inference,results'
    if result_tag!='': tags+=','+result_tag

    r=ck.access({'action':'set',
                 'module_uoa':'env',
                 'tags':tags,
                 'out':'con'})
    if r['return']>0: return r

    lst=r['lst']

    if len(lst)==0:
       return {'return':1, 'error':'can\'t find CK package with MLPerf inference results'}

    path_submission_root=r['dict']['env']['CK_ENV_MLPERF_INFERENCE_RESULTS']

    ck.out('* Path to MLPerf inference results: {}'.format(path_submission_root))

    # Check version
    r=check_mlperf_param(i, 'version', default='1.1')
    if r['return']>0: return r
    version=r['value']

    if version not in ['1.1', '1.0', '0.7', '0.5']:
       return {'return':1, 'error':'"version" is not recognized'}

    ck.out('* MLPerf inference version: {}'.format(version))


    # Check division
    r=check_mlperf_param(i, 'division', default='')
    if r['return']>0: return r
    division=r['value']

    if division not in ['open','closed']:
       return {'return':1, 'error':'"division" must be "open" or "closed"'}

    ck.out('* MLPerf inference division: {}'.format(division))

    path_submission_division=os.path.join(path_submission_root, division)
    if not os.path.isdir(path_submission_division):
       os.makedirs(path_submission_division)

    # Check submitter
    r=check_mlperf_param(i, 'submitter', default='')
    if r['return']>0: return r
    submitter=r['value']

    ck.out('* MLPerf inference submitter: {}'.format(submitter))

    path_submission=os.path.join(path_submission_division, submitter)
    if not os.path.isdir(path_submission):
       os.makedirs(path_submission)



    # SUT base
    r=check_mlperf_param(i, 'system', default='')
    if r['return']>0: return r
    system=r['value']

    #   Attempt to load SUT
    r=ck.access({'action':'load',
                 'module_uoa':cfg['module_deps']['bench.mlperf.system'],
                 'data_uoa':system})
    if r['return']>0: return r
    meta_system_base=r['dict']


    # Target (device: cpu/gpu)
    r=check_mlperf_param(i, 'target', default='cpu')
    if r['return']>0: return r
    target=r['value']

    # Framework
    r=check_mlperf_param(i, 'framework')
    if r['return']>0: return r
    framework=r['value']

    # Framework version (should be taken from the CK later)
    r=check_mlperf_param(i, 'framework_version', default=' ')
    if r['return']>0: return r
    framework_version=r['value'].strip()

    # Framework version (should be taken from the CK later)
    r=check_mlperf_param(i, 'framework_ext', default=' ')
    if r['return']>0: return r
    framework_ext=r['value'].strip()

    ck.out('* Target: {}'.format(target))
    ck.out('* Framework: {}'.format(framework))
    ck.out('* Framework version: {}'.format(framework_version))
    ck.out('* Framework ext: {}'.format(framework_ext))


    # Check model (strict for closed and any for open)
    r=check_mlperf_param(i, 'model', default='')
    if r['return']>0: return r
    model=r['value']

    if division=='closed':
      allowed_models=cfg['closed_division_models'][version]
      if model not in allowed_models:
         return {'return':1, 'error':'closed division model must be in {}'.format(allowed_models)}

    ck.out('* MLPerf inference model: {}'.format(model))

    # Check task
    r=check_mlperf_param(i, 'task', default=' ')
    if r['return']>0: return r
    task=r['value'].strip()

    if task=='':
       # Attempt to detect from the model name
       tasks=cfg['tasks']

       for t in tasks:
           if model in tasks[t]:
              task=t
              break

    if task=='':
       # Fail here with a note
       r=check_mlperf_param(i, 'task', default='')
       if r['return']>0: return r

    ck.out('* MLPerf inference task: {}'.format(task))

    # Check CK workflow to run MLPerf inference
    r=check_mlperf_param(i, 'workflow', default=' ')
    if r['return']>0: return r
    workflow=r['value'].strip()

    ii={'action':'search',
        'module_uoa':cfg['module_deps']['program'],
        'data_uoa':workflow}

    tags=''
    if workflow=='':
       # Add tags to search
       tags='mlperf-inference-benchmark,task-'+task+',framework-'+framework+',target-'+target
       ii['tags']=tags

    r=ck.access(ii)
    if r['return']>0: return r

    lst=r['lst']

    if len(lst)==0:
       return {'return':1, 'error':'can\'t find CK program workflow based on tags "{}"'.format(tags)}

    if len(lst)>1:
       return {'return':1, 'error':'more than one CK program workflow found based on tags "{}"'.format(tags)}

    workflow=lst[0]['data_uoa']
    workflow_path=lst[0]['path']

    ck.out('* MLPerf inference CK workflow: "program:{}"'.format(workflow))
    ck.out('* MLPerf inference CK workflow path: {}'.format(workflow_path))


    # Check scenario
    r=check_mlperf_param(i, 'scenario', default='')
    if r['return']>0: return r
    scenario=r['value']

    if scenario not in cfg['scenarios'][version]:
       return {'return':1, 'error':'"scenario" must be in {}'.format(cfg['scenarios'][version])}

    ck.out('* MLPerf inference division: {}'.format(division))


    # Prepare basic structure
    ck.out('')
    ck.out('Preparing submission directory structure ...')
    paths={}
    for p in cfg['dirs']:
        paths[p]=os.path.join(path_submission, p)

        if not os.path.isdir(paths[p]):
           os.makedirs(paths[p])

    # Prepare final MLPerf system name
    sut=system+'-'+framework

    if framework_version!='':
       sut+='-'+framework_version

    if framework_ext!='':
       sut+='-'+framework_ext

    if framework_ext!='':
       sut+='-'+framework_ext

    if target!='':
       sut+='-'+target

    sut_file=sut+'.json'

    # Prepare SUT JSON and record
    ck.out('')
    ck.out('SUT generated filename: {}'.format(sut_file))

    path_system_file=os.path.join(paths['systems'], sut_file)
    ck.out('SUT path: {}'.format(path_system_file))

    meta_system=meta_system_base
    meta_system['desc']['division']=division
    meta_system['desc']['submitter']=submitter

    r=ck.save_json_to_file({'json_file':path_system_file,
                            'dict':meta_system,
                            'sort_keys':'yes'})
    if r['return']>0: return r

    # Adding directory structure for the given task, model, scenario, workflow
    path_results=os.path.join(path_submission, paths['results'], sut, model, scenario)
    if not os.path.isdir(path_results):
       os.makedirs(path_results)

    # Prepare measurement file (probably after workflow execution based on model package
    path_measurements=os.path.join(path_submission, paths['measurements'], sut, model, scenario)
    if not os.path.isdir(path_measurements):
       os.makedirs(path_measurements)

    # Above: mlperf.conf; user.conf; calibration doc; README.md
    # {sut}_{workflow}_{scenario}.json
    file_measurement=sut+'_'+workflow+'_'+scenario+'.json'
    path_file_measurement=os.path.join(path_measurements, file_measurement)

    dm={}

    r=ck.save_json_to_file({'json_file':path_file_measurement, 
                            'dict':dm,
                            'sort_keys':'yes'})
    if r['return']>0: return r

    path_file_measurement_readme=os.path.join(path_measurements, 'README.md')
    r=ck.save_text_file({'text_file':path_file_measurement_readme, 'string':''})
    if r['return']>0: return r

    # Prepare code
    path_code=os.path.join(path_submission, paths['code'], model, workflow)
    if not os.path.isdir(path_code):
       os.makedirs(path_code)

    path_file_code_readme=os.path.join(path_code, 'README.md')
    r=ck.save_text_file({'text_file':path_file_code_readme, 'string':''})
    if r['return']>0: return r

    ck.out('')
    ck.out('* Path to results: {}'.format(path_results))
    ck.out('* Path to measurements: {}'.format(path_measurements))
    ck.out('* Path to measurement JSON file: {}'.format(path_file_measurement))
    ck.out('* Path to measurement Readme file: {}'.format(path_file_measurement_readme))
    ck.out('* Path to code: {}'.format(path_code))
    ck.out('* Path to code Readme file: {}'.format(path_file_code_readme))

    path_compliance=''
    if division=='closed':
       # Prepare compliance
       path_compliance=os.path.join(path_submission, paths['compliance'], sut, model, scenario)
       if not os.path.isdir(path_compliance):
          os.makedirs(path_compliance)

       ck.out('* Path to compliance: {}'.format(path_compliance))







    return {'return':0}

##############################################################################
# Internal function: check parameter

def check_mlperf_param(i, key, default=''):
    """
    Input:  i [dict] - input
            key - key in input

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              value
            }
    """

    env='CK_MLPERF_INFERENCE_'+key.upper()

    value=i.get(key,'')
    if value=='':
       value=os.environ.get(env,'')
       if value=='':
          value=ck.cfg.get('mlperf_inference_'+key,'')

    if value=='' and default!='':
       value=default

    if value=='':
       return {'return':1, 'error':key+' is not defined (--'+key+', '+env+', ck.cfg["mlperf_'+key+'"])'}

    return {'return':0, 'value':value}
