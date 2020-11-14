#! /usr/bin/python
import ck.kernel as ck
import copy
import re
import argparse

# Platform tag.
platform_tags = 'hikey'

# Number of statistical repetitions.
num_repetitions = 10


def do(i, arg):
  # Detect basic platform info.
  ii = {'action': 'detect',
        'module_uoa': 'platform',
        'out': 'out'}
  r = ck.access(ii)
  if r['return'] > 0:
    return r

  # Host and target OS params.
  hos = r['host_os_uoa']
  hosd = r['host_os_dict']

  tos = r['os_uoa']
  tosd = r['os_dict']
  tdid = r['device_id']

  # Program and command.
  program = 'benchmark-armcl-opencl'
  cmd_key = 'default'

  # Load program meta and desc to check deps.
  ii = {'action': 'load',
        'module_uoa': 'program',
        'data_uoa': program}
  rx = ck.access(ii)
  if rx['return'] > 0:
    return rx
  mm = rx['dict']
  # Get compile-time and run-time deps.
  cdeps = mm.get('compile_deps', {})
  rdeps = mm.get('run_deps', {})

  # Merge rdeps with cdeps for setting up the pipeline (which uses
  # common deps), but tag them as "for_run_time".
  for k in rdeps:
    cdeps[k] = rdeps[k]
    cdeps[k]['for_run_time'] = 'yes'

  # ArmCL libs.
  depl = copy.deepcopy(cdeps['library'])
  if (arg.tos is not None) and (arg.did is not None):
    tos = arg.tos
    tdid = arg.did

  ii = {'action': 'resolve',
        'module_uoa': 'env',
        'host_os': hos,
        'target_os': tos,
        'device_id': tdid,
        'out': 'con',
        'deps': {'library': copy.deepcopy(depl)},
        'quiet': 'yes'
        }
  r = ck.access(ii)
  if r['return'] > 0:
    return r

  udepl = r['deps']['library'].get('choices', [])  # All UOAs of env for ArmCL libs.
  if len(udepl) == 0:
    return {'return': 1, 'error': 'no installed ArmCL libs'}

  # Prepare pipeline.
  cdeps['library']['uoa'] = udepl[0]
  ii = {'action': 'pipeline',
        'prepare': 'yes',
        'dependencies': cdeps,

        'module_uoa': 'program',
        'data_uoa': program,
        'cmd_key': cmd_key,

        'target_os': tos,
        'device_id': tdid,

        'no_state_check': 'yes',
        'no_compiler_description': 'yes',
        'skip_calibration': 'yes',

        'env': {
        },

        'cpu_freq': 'max',
        'gpu_freq': 'max',

        'flags': '-O3',
        'speed': 'no',
        'energy': 'no',

        'skip_print_timers': 'yes',
        'out': 'con'
        }

  r = ck.access(ii)
  if r['return'] > 0:
    return r
  fail = r.get('fail', '')
  if fail == 'yes':
    return {'return': 10, 'error': 'pipeline failed (' + r.get('fail_reason', '') + ')'}

  ready = r.get('ready', '')
  if ready != 'yes':
    return {'return': 11, 'error': 'pipeline not ready'}

  state = r['state']
  tmp_dir = state['tmp_dir']

  # Remember resolved deps for this benchmarking session.
  xcdeps = r.get('dependencies', {})
  # Clean pipeline.
  if 'ready' in r:
    del(r['ready'])
  if 'fail' in r:
    del(r['fail'])
  if 'return' in r:
    del(r['return'])

  pipeline = copy.deepcopy(r)

  # For each lib.*******************************************************
  for lib_uoa in udepl:
    # Load lib.
    ii = {'action': 'load',
          'module_uoa': 'env',
          'data_uoa': lib_uoa}
    r = ck.access(ii)
    if r['return'] > 0:
      return r
    # Get the tags from the version.
    lib_tags = r['dict']['customize']['version']
    # Skip some libs with "in [..]" or "not in [..]".
    lib_tags_firefly = ['17.12-48bc34e', 'master-32b37ec-17.10', 'master-c17f004-18.01']
    lib_tags_hikey = ['17.12-48bc34ea', 'master-32b37ec4-17.10', 'master-c17f004f-18.01']
    if lib_tags not in lib_tags_firefly + lib_tags_hikey:
      continue
    # NB: The baseline "17.10" lib does not support MobileNet.
    if lib_tags[-5:] == '17.10':
      networks = ['alexnet', 'googlenet', 'lenet', 'squeezenet', 'vgg16', 'vgg19']
      compiler_vars = {'EXCLUDE_MOBILENET': 1}
    else:
      networks = ['alexnet', 'googlenet', 'lenet', 'squeezenet', 'vgg16', 'vgg19', 'mobilenet']
      compiler_vars = {}
    compiler_vars['DATATYPE'] = 'DataType::F16'

    max_batch_size = 1
    batch_sizes = range(1, max_batch_size + 1)

    skip_compile = 'no'

    for prof_tags in ['no-prof', 'dvdt-prof']:
      dvdt_prof = 'yes' if prof_tags == 'dvdt-prof' else 'no'

      record_repo = 'local'
      record_uoa = program + '-' + lib_tags + '-' + prof_tags + '-' + platform_tags + '-f16'

      # Prepare pipeline.
      ck.out('---------------------------------------------------------------------------------------')
      ck.out('%s - %s' % (lib_tags, lib_uoa))
      ck.out('%s - \'dvdt_prof\':\'%s\'' % (prof_tags, dvdt_prof))
      ck.out('Experiment - %s:%s' % (record_repo, record_uoa))

      # Prepare autotuning input.
      cpipeline = copy.deepcopy(pipeline)

      # Reset deps and change UOA.
      new_deps = {'library': copy.deepcopy(depl)}

      new_deps['library']['uoa'] = lib_uoa

      jj = {'action': 'resolve',
            'module_uoa': 'env',
            'host_os': hos,
            'target_os': tos,
            'device_id': tdid,
            'deps': new_deps}
      r = ck.access(jj)
      if r['return'] > 0:
        return r

      cpipeline['dependencies'].update(new_deps)

      cpipeline['no_clean'] = skip_compile
      cpipeline['no_compile'] = skip_compile
      cpipeline['compiler_vars'] = compiler_vars

      cpipeline['dvdt_prof'] = dvdt_prof

      cpipeline['cmd_key'] = cmd_key

      ii = {'action': 'autotune',

            'module_uoa': 'pipeline',
            'data_uoa': 'program',

            'choices_order': [
                [
                    '##choices#env#CK_NETWORK'
                ],
                [
                    '##choices#env#CK_BATCH_SIZE'
                ]
            ],
            'choices_selection': [
                {'type': 'loop', 'choice': networks},
                {'type': 'loop', 'choice': batch_sizes},
            ],

            'features_keys_to_process': ['##choices#*'],

            'iterations': -1,
            'repetitions': num_repetitions,

            'record': 'yes',
            'record_failed': 'yes',
            'record_params': {
                'search_point_by_features': 'yes'
            },
            'record_repo': record_repo,
            'record_uoa': record_uoa,

            'tags': ['benchmark-armcl-opencl', platform_tags, lib_tags, prof_tags, 'f16'],

            'pipeline': cpipeline,
            'out': 'con'}

      r = ck.access(ii)
      if r['return'] > 0:
        return r
      fail = r.get('fail', '')
      if fail == 'yes':
        return {'return': 10, 'error': 'pipeline failed (' + r.get('fail_reason', '') + ')'}

      skip_compile = 'yes'

  return {'return': 0}


parser = argparse.ArgumentParser(description='Pipeline')
parser.add_argument("--target_os", action="store", dest="tos")
parser.add_argument("--device_id", action="store", dest="did")
myarg = parser.parse_args()


r = do({}, myarg)
if r['return'] > 0:
  ck.err(r)
