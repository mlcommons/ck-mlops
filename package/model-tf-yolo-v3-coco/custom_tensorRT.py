
import tensorflow as tf
import tensorflow.contrib.tensorrt as trt

def load_graph_tensorrt_custom(params):
  graph_def = tf.compat.v1.GraphDef()
  with tf.gfile.GFile(params["FROZEN_GRAPH"], 'rb') as f:
    graph_def.ParseFromString(f.read())
    tf.import_graph_def(graph_def, name='')
  trt_graph = trt.create_inference_graph(
        input_graph_def=graph_def,
        outputs=["pred_sbbox/concat_2:0", "pred_mbbox/concat_2:0", "pred_lbbox/concat_2:0"],
        max_batch_size=params["BATCH_SIZE"],
        max_workspace_size_bytes=4000000000,
        is_dynamic_op=True if params["TENSORRT_DYNAMIC"]==1 else False,
        precision_mode=params["TENSORRT_PRECISION"]
        )
  tf.import_graph_def(
        trt_graph,
        return_elements=["pred_sbbox/concat_2:0", "pred_mbbox/concat_2:0", "pred_lbbox/concat_2:0"])


def convert_from_tensorrt(tmp_output_dict ):
  output_dict = {}
  output_dict['pred_sbbox/concat_2:0'] = tmp_output_dict[0]
  output_dict['pred_mbbox/concat_2:0']= tmp_output_dict[1]
  output_dict['pred_lbbox/concat_2:0'] = tmp_output_dict[2]
  return output_dict



def get_handles_to_tensors_RT():

  graph = tf.get_default_graph()
  ops = graph.get_operations()
  all_tensor_names = {output.name for op in ops for output in op.outputs}
  return_elements=["import/pred_sbbox/concat_2:0", "import/pred_mbbox/concat_2:0", "import/pred_lbbox/concat_2:0"]
  tensor_dict = []
  for key in return_elements:
    if key in all_tensor_names:
      tensor_dict.append(graph.get_tensor_by_name(key))
  image_tensor =graph.get_tensor_by_name('import/input/input_data:0')
  return tensor_dict, image_tensor
