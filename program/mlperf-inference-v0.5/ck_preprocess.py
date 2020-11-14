#
# Preprocess MLPerf conf templates.
#
# Developers:
# - Anton Lokhmotov, dividiti, 2020
#

import json
import os
import re
from pprint import pprint

def ck_preprocess(i):

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    env=i['env']
    new_env={} # new environment to be added to the run script
    bat='\n'

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']
    remote=tosd.get('remote','')

    if remote=='yes':
       es=tosd['env_set']
    else:
       es=hosd['env_set'] # set or export

    # Access the MODEL_NAME env variable from the model source metadata.
    model_name = deps['weights']['dict']['deps']['model-source']['dict']['customize']['install_env']['MODEL_NAME']
    ck.out('Preprocessing for {} ...'.format(model_name))

    user_conf_template_path = '../user.conf.template'
    user_conf = []
    with open(user_conf_template_path, 'r') as user_conf_template_file:
        user_conf_template = user_conf_template_file.readlines()
        for line in user_conf_template:
            split_line = line.split('=')
            if len(split_line) == 2 and not split_line[0].strip().startswith('#'):
                key = split_line[0].split('.')[-1].strip()
                value = split_line[1].strip()
                conf_to_env_map = {
                    'max_query_count'                  : 'CK_LOADGEN_MAX_QUERY_COUNT',
                    'performance_sample_count_override': 'CK_LOADGEN_BUFFER_SIZE',
                    'samples_per_query'                : 'CK_LOADGEN_SAMPLES_PER_QUERY',
                    'target_latency'                   : 'CK_LOADGEN_TARGET_LATENCY',
                    'target_qps'                       : 'CK_LOADGEN_TARGET_QPS'
                }
                for conf_name, env_name in conf_to_env_map.items():
                    if conf_name == key:
                        env_value = env.get(env_name,'')
                        if env_value != '':
                            line = '{}={}'.format(split_line[0], split_line[1].replace(value, env_value))
                            break
            # Append the original or modified line.
            user_conf.append(line)

    cmd_key = i['misc']['cmd_key']
    run_vars = i['meta']['run_cmds'][cmd_key]['run_vars']
    user_conf_rel_path = run_vars.get('CK_LOADGEN_USER_CONF', '../user.conf.custom') # FIXME: default rel path should be defined in meta.
    user_conf_abs_path = os.path.join(os.path.abspath(os.path.curdir), user_conf_rel_path)
    with open(user_conf_abs_path, 'w') as user_conf_file:
         user_conf_file.writelines(user_conf)

    return {'return':0, 'bat':bat, 'new_env':new_env}

# Do not add anything here!
