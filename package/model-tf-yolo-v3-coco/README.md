# Object Detection - TensorFlow YOLO-v3 Model Package

This package contains an example of a "custom" model for the [`object-detection-tf-py`](https://github.com/ctuning/ck-tensorflow/blob/master/program/object-detection-tf-py/) application.
This application has function hooks that allow anyone to integrate into the application a model that is not structured in the same way as models in the [TensorFlow model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md).
These functions are in two Python files in this package: [`custom_hooks.py`](#custom_hooks) and [`custom_tensorRT.py`](#custom_tensorRT). 

<a href="custom_hooks"></a>
## `custom_hooks.py`

The file has to expose 5 functions:
- `ck_custom_preprocess`, `ck_custom_preprocess_batch`
- `ck_custom_postprocess`, `ck_custom_postprocess_batch`
- `ck_custom_get_tensors`

**NB:** The batch processing functions (`ck_custom_*process_batch`) have the same interface as the non-batch ones (`ck_custom_*process`).
The main difference is in the first dimension of input/output: 
for example, if the non-batch functions work with tensors of shape `[1, H, W, C]`, the batch ones work with tensors of shape `[N, H, W,C]`.

**TODO:** Describe how the `--env.CK_ENABLE_BATCH` flag enables the choice of batch and non-batch functions.

In more detail, the function descriptions and parameters have to follow the following scheme.

### `ck_custom_preprocess`, `ck_custom_preprocess_batch`

These functions are in charge of preparing the input image for the detection.
They must produce the input tensor and some other helper data.

| Input Parameter | Description |
| ---- | ---- |
|`image_files`          | list with all the filenames of the image to process, with full path|
|`iter_num`             | integer with the loop iteration value|
|`processed_image_ids`  | list with the ids of all the processed images, it's an in-out parameter (the function must append to this)|
|`params`               | dictionary with the application parameters |

| Output Parameter | Description |
| ---- | ---- |
|`image_data`           | NumPy array to be fed to the detection graph (input tensor)|
|`processed_image_ids`  | see input parameters|
|`image_size`           | [list of] tuple with the sizes. depends if batch is used or not, if not is a single tuple|
|`original_image`       | [list of] list containing the original images as read before the modification done in preprocessing. may be useless. |


### `ck_custom_postprocess`, `ck_custom_postprocess_batch`

These functions are in charge of producing the output of the detection.
They must read output tensors and produce a `txt` file with the detections, and, if requested, output images with the boxes.
	
| Input Parameter | Description |
| ---- | ---- |
|`image_files`	     | list with all the filenames of the image to process, with full path |
|`iter_num`            | integer with the loop iteration value |
|`image_size`	     | [list of] tuple with the sizes. depends if batch is used or not, if not is a single tuple|
|`original_image`      | [list of] list containing the original images as read before the modification done in preprocessing. may be useless. |
|`image_data`          | NumPy array to be fed to the detection graph (input tensor)|
|`output_dict`         | output tensors. dictionary containing the tensors as "name : value" couples.|
|`category_index`      | dictionary to identify label and categories|
|`params`              | dictionary with the application parameters|

**No Output Parameters**
		
### `ck_custom_get_tensors`

These function is in charge of getting the input and output tensors from the model graph.

**No Input Parameters**

| Output Parameter | Description |
| ---- | ---- |
|`tensor_dict`          | dictionary with the output tensors|
|`input_tensor`         | input tensor|


## `custom_tensorRT.py`

This file contains 3 functions required to support the TensorRT backend:

- `load_graph_tensorrt_custom`
- `convert_from_tensorrt`     
- `get_handles_to_tensors_RT` 

**TODO:** Describe how the `--env.CK_ENABLE_TENSORRT` flag enables the choice the backend.

In more detail, function must support the interfaces as follows:

### `load_graph_tensorrt_custom`:

This function is in charge of loading the graph from a frozen model.
	
| Input Parameter | Description |
| ---- | ---- |
| `params`               | dictionary with the application parameters |

**No Output Parameters**

### `convert_from_tensorrt`
This function is in charge of converting the output to a dictionary (since TensorRT outputs a list, not a dictionary).
	
| Input Parameter | Description |
| ---- | ---- |
|`output_dict`          | Output tensors. if TensorRT, is a list/dictionary containing the output tensors with TensorRT names. |

| Output Parameter | Description |
| ---- | ---- |
|`output_dict`          | Output tensors. dictionary/list containing the tensors as the postprocessing function requires.


### `get_handles_to_tensors_RT`
This function is in charge of getting the input and output tensors from the model graph.

**No Input Parameters**

| Output Parameter | Description |
| ---- | ---- |
|`tensor_dict`          | dictionary with the output tensors|
|`input_tensor`         | input tensor|

The internal tensor representation is strictly linked to the model, and the
application is completely agnostic in this aspect. The programmer is in charge
to keep the coherency between the preprocess, get tensor and postprocess
functions.
