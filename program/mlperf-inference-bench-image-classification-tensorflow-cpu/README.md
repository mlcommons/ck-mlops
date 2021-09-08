# MLPerf inference benchmark workflow

* Automation: [CK](https://github.com/ctuning/ck)
* Task: image classification
* Dataset: ImageNet
* Framework: [ONNX runtime](https://github.com/tensorflow/tensorflow)
* Models: TensorFlow format
* Target device: CPU

# Preparation

* System prerequisites
  - [x8664; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/x8664-ubuntu.md)

* [Common setup](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/common.md)
* [Framework installation (CPU)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-tf.md)

## Dataset

* [Installation](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/datasets/imagenet2012.md)

## Models

```bash
ck install package --tags=model,image-classification,mlperf,tensorflow,resnet50
```

## Python prerequisites

```bash
ck run program:mlperf-inference-bench-image-classification-tensorflow-cpu \
        --cmd_key=install-python-requirements
```

# Test accuracy

## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-tensorflow-cpu \
        --cmd_key=accuracy-offline
```

Customize it:
```bash
ck run program:mlperf-inference-bench-image-classification-tensorflow-cpu \
        --cmd_key=accuracy-offline \
        --env.EXTRA_OPS="--count=100 --threads 16 --max-batchsize 4"

```

## Server

```bash
ck run program:mlperf-inference-bench-image-classification-tensorflow-cpu \
        --cmd_key=accuracy-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-tensorflow-cpu \
        --cmd_key=accuracy-singlestream
```


# Test performance 


## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-tensorflow-cpu \
        --cmd_key=performance-offline
```

## Server

```bash
ck run program:mlperf-inference-bench-image-classification-tensorflow-cpu \
        --cmd_key=performance-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-tensorflow-cpu \
        --cmd_key=performance-singlestream
```
