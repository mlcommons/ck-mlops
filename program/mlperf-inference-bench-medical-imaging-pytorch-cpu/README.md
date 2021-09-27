# MLPerf inference benchmark workflow

* Automation: [CK](https://github.com/ctuning/ck)
* Task: medical imaging (image segmentation)
* Dataset: BraTS 2019
* Framework: [ONNX runtime](https://github.com/microsoft/onnxruntime)
* Models: ONNX format
* Target device: CPU

# Preparation

* System prerequisites
  - [x8664; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/x8664-ubuntu.md)

* [Common setup](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/common.md)
* [Framework installation (CPU)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-onnx.md)

## Dataset

TODO: fill out this guide (BraTS is not openly available so it can only be detected as soft)

* [Installation](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/datasets/brats.md)

## Models

```bash
ck install package --tags=ml-model,medical-imaging,3d-unet
```
```

## Python prerequisites

```bash
ck run program:mlperf-inference-bench-medical-imaging-onnx-cpu \
        --cmd_key=install-python-requirements
```

# Test accuracy

## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-medical-imaging-onnx-cpu \
        --cmd_key=accuracy-offline
```

## Server

```bash
ck run program:mlperf-inference-bench-medical-imaging-onnx-cpu \
        --cmd_key=accuracy-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-medical-imaging-onnx-cpu \
        --cmd_key=accuracy-singlestream
```


# Test performance 


## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-medical-imaging-onnx-cpu \
        --cmd_key=performance-offline
```

## Server

```bash
ck run program:mlperf-inference-bench-medical-imaging-onnx-cpu \
        --cmd_key=performance-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-medical-imaging-onnx-cpu \
        --cmd_key=performance-singlestream
```
