# MLPerf inference benchmark workflow

* Automation: [CK](https://github.com/mlcommons/ck)
* Task: medical imaging (image segmentation)
* Dataset: BraTS 2019
* Framework: [ONNX runtime](https://github.com/microsoft/onnxruntime)
* Models: ONNX format
* Target device: CPU

# Preparation

* System prerequisites
  - [x8664; Ubuntu 20.04 (system deps)](https://github.com/mlcommons/ck/blob/master/docs/mlperf-automation/platform/x8664-ubuntu.md)

* [Common setup](https://github.com/mlcommons/ck/blob/master/docs/mlperf-automation/setup/common.md)
* [Framework installation (PyTorch - to preprocess a dataset)](https://github.com/mlcommons/ck/blob/master/docs/mlperf-automation/setup/framework-pytorch.md)

## Dataset

* [Installation](https://github.com/mlcommons/ck/blob/master/docs/mlperf-automation/datasets/brats2019.md)

## Models

```bash
ck install package --tags=ml-model,medical-imaging,3d-unet,pytorch
```

## Python prerequisites

```bash
ck run program:mlperf-inference-bench-medical-imaging-pytorch-cpu \
        --cmd_key=install-python-requirements
```

# Test accuracy

## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-medical-imaging-pytorch-cpu \
        --cmd_key=accuracy-offline
```

## Server

```bash
ck run program:mlperf-inference-bench-medical-imaging-pytorch-cpu \
        --cmd_key=accuracy-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-medical-imaging-pytorch-cpu \
        --cmd_key=accuracy-singlestream
```


# Test performance 


## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-medical-imaging-pytorch-cpu \
        --cmd_key=performance-offline
```

## Server

```bash
ck run program:mlperf-inference-bench-medical-imaging-pytorch-cpu \
        --cmd_key=performance-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-medical-imaging-pytorch-cpu \
        --cmd_key=performance-singlestream
```
