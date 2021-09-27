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
* [Framework installation (ONNX - CPU)](https://github.com/mlcommons/ck/blob/master/docs/mlperf-automation/setup/framework-onnx.md)
* [Framework installation (PyTorch - to preprocess a dataset)](https://github.com/mlcommons/ck/blob/master/docs/mlperf-automation/setup/framework-pytorch.md)

## Dataset

* [Installation](https://github.com/mlcommons/ck/blob/master/docs/mlperf-automation/datasets/brats2019.md)

## Models

```bash
ck install package --tags=ml-model,medical-imaging,3d-unet,onnx
```

## Python prerequisites

Several packages are required by the nnUnet library, which is
used in the reference implementation.

```bash
ck run program:mlperf-inference-bench-medical-imaging-onnx-cpu \
        --cmd_key=install-python-requirements
```

# Test accuracy

For both accuracy and performance mode, preprocessing is done by
the PyTorch model prior to running and may take up to 1-2 minutes.

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

Note: running may take up to 10-30s per sample on a CPU.

## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-medical-imaging-onnx-cpu \
        --cmd_key=performance-offline
```

Customize QSL size for performance mode with `CK_LOADGEN_PERFORMANCE_COUNT`:
```bash
ck run program:mlperf-inference-bench-medical-imaging-onnx-cpu \
        --cmd_key=performance-offline \
        --env.CK_LOADGEN_PERFORMANCE_COUNT=8
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
