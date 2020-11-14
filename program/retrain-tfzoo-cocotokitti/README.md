# CK Object Detection Retraining Utilities

Warning: Not all the operations in this program can be automatized, some jobs in the pipeline MUST be manually handled by the user.
Moreover, this will work only with models coming from the 
[tensorflow zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md).

## Prerequisites

### Install CK

Please follow the [CK installation instructions](https://github.com/ctuning/ck#installation).

### Pull CK repositories

```bash
$ ck pull repo:ck-tensorflow
```

### Install TensorFlow

Install TensorFlow v1.14 from source (built with Bazel):
```bash
$ ck install package --tags=lib,tensorflow,v1.14,vsrc,vcpu
```
or from a binary `x86_64` package (installed via `pip`):
```bash
$ ck install package --tags=lib,tensorflow,v1.14,vprebuilt,vcpu
```
Replace `vcpu` with `vcuda` to install TensorFlow with GPU support.

Or you can choose interactively from any available version of TensorFlow:
```bash
$ ck install package --tags=lib,tensorflow
```

### Install TensorFlow models
```bash
$ ck install package --tags=tensorflow,model,api
```


Install one or more object detection model package:
```bash
$ ck install package --tags=tf,model,object-detection
```

### Datasets
Install the kitti full dataset
```bash
$ ck install package --tags=dataset,object-detection,kitti-full
```

### Other Dependencies
Install the pycocotool 

```bash
$ ck install package --tags=tool,coco
```

## Programs
There are three different programs in this pipeline:

| Program | Task |
| ---- | ---- |
| a:create_dataset | creates a tf compatible record from the kitti dataset, and copies the required pipeline and checkpoint from the model folder to the working directory |
| b:retrain | performs the retraining or the fine tuning, according to the (manual) configuration of the pipeline |
| c:export_model | creates a frozen_graph from a checkpoint |

In order to obtain a completely working model, you will need to run them in this order and add some manual work between
the dataset creation and the retrain.

### a:create_dataset

This program will prepare the required data for the retraining.
All the parameters are provided by default ( **I am not sure about the CK_OUTPATH, which is an empty string, 
if it means current working directory or if i just forgot it, need to test it**). They can be overridden by setting the 
appropriate CK env variables.

After the create dataset, the pipeline.config is copied in the /tmp folder, which is the working directory.
Now you have to manually edit the file. There are some more mechanical tasks, and other less intuitive and it may not work. 
In that case, it is possible that they changed some parameters in the tensorflow object detection repository, and you may have
to search on google how to edit the pipeline in order to retrain/finetune.

The mandatory (and easy) tasks that must be performed are:
- Change the dataset-related info in the first block. In particular, we target the kitti dataset so this have 7 classes
(car,van,truck,pedestrian,person_sitting,cyclist,tram). Moreover, the images in the dataset have a different shape, so the
resizer must be set at 375(height)*1242(width).
- Modify the path wherever the PATH_TO_BE_CONFIGURED string appears. You must use ABSOLUTE path.
- If you want to retrain, you will have to provide a starting checkpoint (again, you will need an absolute path). And if not set
you will need to set the from_detection_checkpoint: true and load_all_detection_checkpoint_vars: true

Other possible issues (from my experience):
- if a schedule with step 0 appears in the pipeline.config, in the manual_step_learning_rate, has to be removed. It is an old
version of the API and has been removed and it causes the training to fail.
- with lowproposals models, the fiels "second_stage_batch_size" has to be added, immediately after "first_stage_objectness_loss_weight",
with a value lower than "first_stage_max_proposals".


### b:retrain

This program will perform the actual retraining. All the parameters are set by default beside one, the number of steps for the
retraining.
This must be set when calling the program, using the CK env variable 'CK_NUM_STEPS'.

### c:export_model

This program will create the frozen graph, with the checkpoints and everything that is needed to "restart" in the future, and
also creating the graph that can be used for inference.
It will require a mandatory parameter, 'CK_CHECKPOINT_PREFIX', that will select the checkpoint to use for the export. it must
be one of the checkpoints in the 'model.ckpt' folder, contained in the working directory (called tmp).
The exported graph will be crated in the 'output_dir' inside the tmp folder. This can be overridden by changing the 'CK_OUT_DIR' 
env variable.
All the other parameters are set by default, and can be overridden by using the appropriate CK variables

