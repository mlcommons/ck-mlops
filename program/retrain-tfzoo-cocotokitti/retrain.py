from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#from absl import flags

import tensorflow as tf
import os

from object_detection import model_hparams
from object_detection import model_lib


## commented out because i want to "save" what the parameters are meaning, could be removed otherwise
#flags.DEFINE_string(
#    'model_dir', None, 'Path to output model directory '
#    'where event and checkpoint files will be written.')
#flags.DEFINE_string('pipeline_config_path', None, 'Path to pipeline config '
#                    'file.')
#flags.DEFINE_integer('num_train_steps', None, 'Number of train steps.')
#flags.DEFINE_boolean('eval_training_data', False,
#                     'If training data should be evaluated for this job. Note '
#                     'that one call only use this in eval-only mode, and '
#                     '`checkpoint_dir` must be supplied.')
#flags.DEFINE_integer('sample_1_of_n_eval_examples', 1, 'Will sample one of '
#                     'every n eval input examples, where n is provided.')
#flags.DEFINE_integer('sample_1_of_n_eval_on_train_examples', 5, 'Will sample '
#                     'one of every n train input examples for evaluation, '
#                     'where n is provided. This is only used if '
#                     '`eval_training_data` is True.')
#flags.DEFINE_string(
#    'hparams_overrides', None, 'Hyperparameter overrides, '
#    'represented as a string containing comma-separated '
#    'hparam_name=value pairs.')
#flags.DEFINE_string(
#    'checkpoint_dir', None, 'Path to directory holding a checkpoint.  If '
#    '`checkpoint_dir` is provided, this binary operates in eval-only mode, '
#    'writing resulting metrics to `model_dir`.')
#flags.DEFINE_boolean(
#    'run_once', False, 'If running in eval-only mode, whether to run just '
#    'one round of eval vs running continuously (default).'
#)
#FLAGS = flags.FLAGS


def main(unused_argv):
  params = {}
  params["PIPELINE_FILE"] = 'pipeline.config'
  params["MODEL_DIR"] = 'model.ckpt' #output directory
  params["NUM_STEPS"] = int (os.getenv("CK_NUM_STEPS",'1'))
  params["EVAL_TRAIN_DATA"] = os.getenv("CK_EVAL_TRAIN_DATA",False)
  params["SAMPLE_1_OF_N_EVAL_EXAMPLES"] =int ( os.getenv("CK_SAMPLE_1_OF_N_EVAL_EXAMPLES",1))
  params["SAMPLE_1_OF_N_TRAIN_EXAMPLES"] =int ( os.getenv("CK_SAMPLE_1_OF_N_TRAIN_EXAMPLES",5))
  params["HYPERPARAMS_OVERRIDE"] = os.getenv("CK_HYPERPARAMS_OVERRIDE",None)
  params["CHECKPOINT_DIR"] = os.getenv("CK_CHECKPOINT_DIR",None)
  params["RUN_ONCE"] = os.getenv("CK_RUN_ONCE",None)
  #flags.mark_flag_as_required('model_dir')
  #flags.mark_flag_as_required('pipeline_config_path')
  config = tf.estimator.RunConfig(params["MODEL_DIR"])

  train_and_eval_dict = model_lib.create_estimator_and_inputs(
      run_config=config,
      hparams=model_hparams.create_hparams(params["HYPERPARAMS_OVERRIDE"]),
      pipeline_config_path=params["PIPELINE_FILE"],
      train_steps=params["NUM_STEPS"],
      sample_1_of_n_eval_examples=params["SAMPLE_1_OF_N_EVAL_EXAMPLES"],
      sample_1_of_n_eval_on_train_examples=(
          params["SAMPLE_1_OF_N_TRAIN_EXAMPLES"]))
  estimator = train_and_eval_dict['estimator']
  train_input_fn = train_and_eval_dict['train_input_fn']
  eval_input_fns = train_and_eval_dict['eval_input_fns']
  eval_on_train_input_fn = train_and_eval_dict['eval_on_train_input_fn']
  predict_input_fn = train_and_eval_dict['predict_input_fn']
  train_steps = train_and_eval_dict['train_steps']

  if params["CHECKPOINT_DIR"]:
    if params["EVAL_TRAIN_DATA"]:
      name = 'training_data'
      input_fn = eval_on_train_input_fn
    else:
      name = 'validation_data'
      # The first eval input will be evaluated.
      input_fn = eval_input_fns[0]
    if params["RUN_ONCE"]:
      estimator.evaluate(input_fn,
                         steps=None,
                         checkpoint_path=tf.train.latest_checkpoint(
                             params["CHECKPOINT_DIR"]))
    else:
      model_lib.continuous_eval(estimator, params["CHECKPOINT_DIR"], input_fn,
                                train_steps, name)
  else:
    train_spec, eval_specs = model_lib.create_train_and_eval_specs(
        train_input_fn,
        eval_input_fns,
        eval_on_train_input_fn,
        predict_input_fn,
        train_steps,
        eval_on_train_data=False)

    # Currently only a single Eval Spec is allowed.
    tf.estimator.train_and_evaluate(estimator, train_spec, eval_specs[0])


if __name__ == '__main__':
  tf.app.run()






