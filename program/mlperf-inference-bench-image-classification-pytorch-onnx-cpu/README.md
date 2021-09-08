# MLPerf inference benchmark workflow

* Automation: [CK](https://github.com/ctuning/ck)
* Task: image classification
* Dataset: ImageNet
* Framework: [PyTorch](https://pytorch.org)
* Models: ONNX format
* Target device: CPU

# Preparation

* System prerequisites
  - [x8664; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/x8664-ubuntu.md)

* [Common setup](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/common.md)
* [Framework installation (CPU)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-pytorch.md)
  - MLPerf v1.1 worked with PyTorch 1.5.0 and TorchVision 0.6.0

## Dataset

* [Installation](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/datasets/imagenet2012.md)

## Models

```bash
ck install package --tags=model,image-classification,mlperf,onnx,resnet50,v1.5-opset-8
```

You can install a newer model with Opset-11 (models and other components can coexist in CK) 
though it doesn't with MLPerf inference v1.1:
```bash
ck install package --tags=model,image-classification,mlperf,onnx,resnet50,v1.5-opset-11
```

## Python prerequisites

```bash
ck run program:mlperf-inference-bench-image-classification-pytorch-onnx-cpu \
        --cmd_key=install-python-requirements
```

# Test accuracy

## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-pytorch-onnx-cpu \
        --cmd_key=accuracy-offline
```

Customize it:
```bash
ck run program:mlperf-inference-bench-image-classification-pytorch-onnx-cpu \
        --cmd_key=accuracy-offline \
        --env.EXTRA_OPS="--count=100 --threads 4 --max-batchsize 2"

```

## Server

```bash
ck run program:mlperf-inference-bench-image-classification-pytorch-onnx-cpu \
        --cmd_key=accuracy-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-pytorch-onnx-cpu \
        --cmd_key=accuracy-singlestream
```


# Test performance 


## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-pytorch-onnx-cpu \
        --cmd_key=performance-offline
```

## Server

```bash
ck run program:mlperf-inference-bench-image-classification-pytorch-onnx-cpu \
        --cmd_key=performance-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-pytorch-onnx-cpu \
        --cmd_key=performance-singlestream
```
