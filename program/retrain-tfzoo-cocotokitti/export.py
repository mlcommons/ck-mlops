import os
import sys
import tensorflow as tf
from google.protobuf import text_format
from object_detection import exporter
from object_detection.protos import pipeline_pb2



def main(_):
  params = {}
  params["PIPELINE_FILE"] = 'pipeline.config'  ##path to the pipeline.config that should be already in the /tmp folder, hardcoded
  params["INPUT_TENSOR"] = 'image_tensor' ## we handle only tf_zoo at the moment.
  params["TRAINED_MODEL_CHKPT"] = os.getenv("CK_CHECKPOINT_PREFIX",None) ###mandatory parameter, cannot be hardcoded in any way. it's the "model.ckpt-####### that comes out from the training. has to be chosen by the user
  if params["TRAINED_MODEL_CHKPT"] == None:
    print ("you need to provide the checkpoint prefix as --env.CK_CHECKPOINT_PREFIX when running this program. the value is the \"model.ckpt-#######\" created by step by that you want to export as frozen graph")
    sys.exit()

  CWD = os.getcwd()
  params["OUTPUT_DIR"] = os.getenv("CK_OUT_DIR",os.path.join(CWD,'output_dir')) ## will be created, inside tmp

  ## three params unknown to me, taken from the original application in tensorflow api/research/object_detection/export_inference_graph.py. I force setup as default in the original program. Look there for more information.
  params["CONFIG_OVERRIDE"] = os.getenv("CK_CONFIG_OVERRIDE",'') 
  params["WRITE_INFERENCE"] = os.getenv("CK_WRITE_INFERENCE",False)
  params["INPUT_SHAPE"] = os.getenv("CK_INPUT_SHAPE",None)


  pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
  with tf.gfile.GFile(params["PIPELINE_FILE"], 'r') as f:
    text_format.Merge(f.read(), pipeline_config)
  text_format.Merge(params["CONFIG_OVERRIDE"], pipeline_config)
  if params["INPUT_SHAPE"]:
    input_shape = [
        int(dim) if dim != '-1' else None
        for dim in params["INPUT_SHAPE"].split(',')
    ]
  else:
    input_shape = None
  exporter.export_inference_graph(
      params["INPUT_TENSOR"], pipeline_config, 'model.ckpt/model.ckpt-{}'.format(params["TRAINED_MODEL_CHKPT"]),
      params["OUTPUT_DIR"], input_shape=input_shape,
      write_inference_graph=params["WRITE_INFERENCE"])


if __name__ == '__main__':
  tf.app.run()
