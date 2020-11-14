# TensorFlow object-detection program

## Pre-requisites

### Repositories

```bash
$ ck pull repo:ck-object-detection
$ ck pull repo:ck-tensorflow
```

### TensorFlow

Install from source:
```bash
$ ck install package:lib-tensorflow-1.10.1-src-{cpu,cuda}
```
or from a binary `x86_64` package:
```bash
$ ck install package:lib-tensorflow-1.10.1-{cpu,cuda}
```

Or you can choose from different available version of TensorFlow packages:
```bash
$ ck install package --tags=lib,tensorflow
```

### TensorFlow models
```bash
$ ck install ck-tensorflow:package:tensorflowmodel-api
```

Install one or more object detection model package:
```bash
$ ck install package --tags=tensorflowmodel,object-detection

 0) tensorflowmodel-object-detection-ssd-resnet50-v1-fpn-sbp-640x640-coco  Version 20170714  (09baac5e6f931db2)
 1) tensorflowmodel-object-detection-ssd-mobilenet-v1-coco  Version 20170714  (385831f88e61be8c)
```

### Datasets
```bash
$ ck install package --tags=dataset,object-detection
```

**NB:** If you have previously installed the `coco` dataset, you should probably renew them:
```bash
$ ck refresh env:{dataset-env-uoa}
```
where `dataset-env-uoa` is one of the env identifiers returned by:
```bash
$ ck show env --tags=dataset,coco
```

## Running

```bash
$ ck run program:ck-mlperf-tf-object-detection
```

### Program parameters

#### `CK_BATCH_COUNT`

The number of batches to be processed.

Default: `1`

#### `CK_BATCH_SIZE`

The number of images in each batch

Default: `1`

#### `CK_ENV_TENSORFLOW_MODEL_FROZEN_GRAPH`

The path to the graph to run the inference

Default: set by CK

#### `CK_ENV_TENSORFLOW_MODEL_LABELMAP_FILE`

File with the model labelmap file

Default: set by CK

#### `CK_ENV_TENSORFLOW_MODEL_DATASET_TYPE`

Type of the dataset (coco,kitti,...) that is used for the inference

Default: set by CK

#### `CK_ENV_IMAGE_WIDTH` and `CK_ENV_IMAGE_HEIGHT`

The dimensions for the resize of the images, for the preprocessing

Default: set by CK, according to the selected model

#### `CK_ENV_DATASET_IMAGE_DIR`

Path to the directory with the images

Default: set by CK

#### `CK_ENV_DATASET_TYPE`

Type of dataset used for the program run

Default: set by CK

#### `CK_ENV_DATASET_ANNOTATIONS_PATH`

Path to the file with the annotations

Default: set by CK

#### `CK_PROFILE`

mlperf profile to select for the run

Default: default\_tf\_object\_det\_zoo

#### `CK_SCENARIO`

mlperf scenario of the run

Default: Offline

#### `CK_NUM_THREADS`

Number of threads used in mlperf

Default: `1`

#### `CK_TIME`

mlperf parameter time to scan in seconds

Default: `60`

#### `CK_QPS`

mlperf target qps estimate

Default: `100`

#### `CK_ACCURACY`

mlperf variable used to enable the accuracy pass

Default: 'YES'

#### `CK_CACHE`

mlperf variable used to enable the reuse of preprocessed numpy files. enable ONLY when processing the same model in more than 1 run

Default: `0`

#### `CK_QUERIES_SINGLE` `CK_QUERIES_MULTI` `CK_QUERIES_OFFLINE`

mlperf variables with the queries for the different scenarios

Defaults: `1024` `24576` `24576`

#### `CK_MAX_LATENCY`

mlperf variable with the max latency in the 99pct tile

Default: `0.1`


