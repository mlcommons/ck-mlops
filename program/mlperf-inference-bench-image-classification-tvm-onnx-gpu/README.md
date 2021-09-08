# MLPerf inference benchmark workflow

* Automation: [CK](https://github.com/ctuning/ck)
* Task: image classification
* Framework: [TVM](https://github.com/apache/tvm)
* Dataset: ImageNet
* Models: ONNX format
* Target device: GPU (CUDA)

# Preparation

* System prerequisites
  - [x8664; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/x8664-ubuntu.md)
  - [Raspberry Pi 4; Arm64; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/rpi4-ubuntu.md)
  - [Nvidia Jetson Nano; Arm64; Ubuntu 18.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/nvidia-jetson-nano.md)

* [Common setup](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/common.md)
* [Framework installation (ONNX - to load native models)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-onnx.md)
* [Framework installation (TVM (GPU))](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-tvm.md)

## Dataset

* [Installation](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/datasets/imagenet2012.md)

## Models

```bash
ck install package --tags=model,image-classification,mlperf,onnx,resnet50,v1.5-opset-11
```

You can also install a slightly older (original) model with Opset-8 (models and other components can coexist in CK):
```bash
ck install package --tags=model,image-classification,mlperf,onnx,resnet50,v1.5-opset-8
```

## Python prerequisites

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-gpu \
        --cmd_key=install-python-requirements
```

# Test accuracy

## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-gpu \
        --cmd_key=accuracy-offline
```

Customize it:
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-gpu \
        --cmd_key=accuracy-offline \
        --env.MLPERF_TVM_EXECUTOR=graph \
        --env.EXTRA_OPS="--count=100 --threads 8 --max-batchsize 1"

```

## Server

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-gpu \
        --cmd_key=accuracy-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-gpu \
        --cmd_key=accuracy-singlestream
```


# Test performance 


## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-gpu \
        --cmd_key=performance-offline
```

## Server

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-gpu \
     --cmd_key=performance-server \
     --env.EXTRA_OPS="--threads 8 --max-batchsize 1 --time 100 --qps 400" 
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-gpu \
        --cmd_key=performance-singlestream
```
