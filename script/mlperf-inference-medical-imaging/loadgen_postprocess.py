#
# MLPerf inference; medical imaging; postprocessing
#
# Copyright (c) 2019 cTuning foundation.
# Copyright (c) 2021 OctoML, Inc.
#
# TBD:
#   * Grigori Fursin (20210511): this script has to be reimplemented and documented
#

import os
import json
import re
import sys
from subprocess import check_output

MLPERF_LOG_ACCURACY_JSON = 'mlperf_log_accuracy.json'
MLPERF_LOG_DETAIL_TXT    = 'mlperf_log_detail.txt'
MLPERF_LOG_SUMMARY_TXT   = 'mlperf_log_summary.txt'
MLPERF_LOG_TRACE_JSON    = 'mlperf_log_trace.json'
MLPERF_USER_CONF         = 'user.conf'
MLPERF_AUDIT_CONF        = 'audit.config'
ACCURACY_TXT             = 'accuracy.txt'

MLPERF_LOG_RESULTS_JSON = 'results.json'


def ck_postprocess(i):
  print('\n--------------------------------')

  env               = i['env']

  is_accuracy = env.get('CK_LOADGEN_ACCURACY','').lower()=='on'

  deps              = i['deps']
  SIDELOAD_JSON     = env.get('CK_LOADGEN_SIDELOAD_JSON', '')
  include_trace     = env.get('CK_LOADGEN_INCLUDE_TRACE', '') in ('YES', 'Yes', 'yes', 'TRUE', 'True', 'true', 'ON', 'On', 'on', '1')
  inference_src_env = deps['mlperf-inference-src']['dict']['env']
  MLPERF_MAIN_CONF  = inference_src_env['CK_ENV_MLPERF_INFERENCE_MLPERF_CONF']

  save_dict = {}

  # Save logs.
  mlperf_log_dict   = save_dict['mlperf_log'] = {}
  mlperf_conf_dict  = save_dict['mlperf_conf'] = {}

  with open(MLPERF_LOG_ACCURACY_JSON, 'r') as accuracy_file:
    mlperf_log_dict['accuracy'] = json.load(accuracy_file)

  with open(MLPERF_LOG_SUMMARY_TXT, 'r') as summary_file:
    unstripped_summary_lines = summary_file.readlines()
    mlperf_log_dict['summary'] = unstripped_summary_lines

    save_dict['parsed_summary'] = {}
    parsed_summary = save_dict['parsed_summary']
    for line in unstripped_summary_lines:
      pair = line.strip().split(': ', 1)
      if len(pair)==2:
        parsed_summary[ pair[0].strip() ] = pair[1].strip()

  with open(MLPERF_LOG_DETAIL_TXT, 'r') as detail_file:
    mlperf_log_dict['detail'] = detail_file.readlines()

  if include_trace and os.stat(MLPERF_LOG_TRACE_JSON).st_size!=0:
    with open(MLPERF_LOG_TRACE_JSON, 'r') as trace_file:
      mlperf_log_dict['trace'] = json.load(trace_file)
  else:
    mlperf_log_dict['trace'] = {}

  for conf_path in (MLPERF_MAIN_CONF, MLPERF_USER_CONF, MLPERF_AUDIT_CONF):
    if os.path.exists( conf_path ):
      with open(conf_path, 'r') as conf_fd:
        mlperf_conf_dict[ os.path.basename(conf_path) ] = conf_fd.readlines()

  # Check accuracy in accuracy mode.
  # NB: Used to be just (mlperf_log_dict['accuracy'] != []) but this proved
  # to be unreliable with compliance TEST01 which samples accuracy.
  accuracy_mode = (save_dict['parsed_summary'] == {})
  if accuracy_mode:
    medical_imaging_dir = os.path.join(inference_src_env['CK_ENV_MLPERF_INFERENCE'],
                                       'vision', 'medical_imaging', '3d-unet-brats19')

    # Fix for older version of inference repo
    if not os.path.isdir(medical_imaging_dir):
        medical_imaging_dir = os.path.join(inference_src_env['CK_ENV_MLPERF_INFERENCE'],
                                           'vision', 'medical_imaging', '3d-unet')

    # Add pandas and nnUnet to path
    python_path = [
        deps['lib-python-pandas']['dict']['env']['PYTHONPATH'].split(':')[0],
        os.path.join(medical_imaging_dir, "nnUnet")
    ]
    accuracy_script_env_vars = {}
    accuracy_script_env_vars['PYTHONPATH'] = ':'.join(python_path)

    accuracy_script = os.path.join(medical_imaging_dir, 'accuracy-brats.py')

    command = [ deps['lib-python-loadgen']['dict']['deps']['python']['dict']['env']['CK_ENV_COMPILER_PYTHON_FILE'], accuracy_script ]

    print('------')
    print(command)
    print('')
    output = check_output(command, cwd=medical_imaging_dir, env=accuracy_script_env_vars).decode('utf-8')
    print(output)
    print('------')

    with open(ACCURACY_TXT, 'w') as accuracy_file:
      accuracy_file.write(output)

    matchObj  = re.search(r'Accuracy\:\s*mean\s*=\s*([\d\.]+),\s*whole tumor\s*=\s*([\d\.]+),\s*tumor core\s*=\s*([\d\.]+),\s*enhancing tumor\s*=\s*([\d\.]+)', output)
    save_dict['mean']            = float( matchObj.group(1) )
    save_dict['whole tumor']     = float( matchObj.group(2) )
    save_dict['tumor core']      = float( matchObj.group(3) )
    save_dict['enhancing tumor'] = float( matchObj.group(4) )

  # for scenario in [ 'SingleStream', 'MultiStream', 'Server', 'Offline' ]:
  #   scenario_key = 'TestScenario.%s' % scenario
  #   scenario = save_dict['results'].get(scenario_key, None)
  #   if scenario: # FIXME: Assumes only a single scenario is valid.
  #     save_dict['execution_time_s']  = scenario.get('took', 0.0)
  #     save_dict['execution_time_ms'] = scenario.get('took', 0.0) * 1000
  #     save_dict['percentiles'] = scenario.get('percentiles', {})
  #     save_dict['qps'] = scenario.get('qps', 0)
  #     if accuracy_mode:
  #       ck.out('mAP=%.3f%% (from the results for %s)' % (scenario.get('mAP', 0.0) * 100.0, scenario_key))

  # save_dict['execution_time'] = save_dict['execution_time_s']

  if SIDELOAD_JSON:
    if os.path.exists(SIDELOAD_JSON):
      with open(SIDELOAD_JSON, 'r') as sideload_fd:
        sideloaded_data = json.load(sideload_fd)
    else:
        sideloaded_data = {}
    save_dict['sideloaded_data'] = sideloaded_data


  # Read results.json if exists
  if os.path.isfile('results.json'):
      with open(MLPERF_LOG_RESULTS_JSON, 'r') as fresults:
        save_dict['results'] = json.load(fresults)

  # Record to tmp-ck-timer.json file that will be saved in CK experiments
  with open('tmp-ck-timer.json', 'w') as save_file:
    json.dump(save_dict, save_file, indent=2, sort_keys=True)

  print('--------------------------------\n')
  return {'return': 0}

