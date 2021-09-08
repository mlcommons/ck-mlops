# MLPerf inference benchmark workflow

* Automation: [CK](https://github.com/ctuning/ck)
* Task: image classification
* Framework: [TVM](https://github.com/apache/tvm)
* Dataset: ImageNet
* Models: ONNX format
* Target device: CPU

# Preparation

* System prerequisites
  - [x8664; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/x8664-ubuntu.md)
  - [Raspberry Pi 4; Arm64; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/rpi4-ubuntu.md)
  - [Nvidia Jetson Nano; Arm64; Ubuntu 18.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/nvidia-jetson-nano.md)

* [Common setup](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/common.md)
* [Framework installation (ONNX - to load native models)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-onnx.md)
* [Framework installation (TVM)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-tvm.md)

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
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-cpu \
        --cmd_key=install-python-requirements
```

# Test accuracy

## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-cpu \
        --cmd_key=accuracy-offline
```

Customize it:
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-cpu \
        --cmd_key=accuracy-offline \
        --env.MLPERF_TVM_EXECUTOR=graph \
        --env.MLPERF_TVM_TARGET="llvm" \
        --env.OMP_NUM_THREADS=1 \
        --env.EXTRA_OPS="--count=100 --threads 8 --max-batchsize 1"

```

* You can delete compiled model using flags ```--env.MLPERF_DELETE_COMPILED_MODEL=YES``` or ```--clean```
* You can use your own compatible model by adding --model flag to EXTRA_OPS: ```--env.EXTRA_OPS="--model {FULL PATH}"```
* You can apply best sequence of transformation from autotuning as follows:
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-cpu \
        --cmd_key=performance-offline \
        --clean \
        --env.MLPERF_TVM_EXECUTOR=graph \
        --env.MLPERF_TVM_TARGET="llvm -mcpu=znver3" \
        --env.MLPERF_TVM_TRANSFORM_LAYOUT=YES \
        --env.MLPERF_TVM_APPLY_HISTORY="/tmp/tvm-autotuning-history.json" \
        --env.OMP_NUM_THREADS=1 \
        --env.EXTRA_OPS="--threads 24 --max-batchsize 1 --qps 650 --time 650"
```


## Server

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-cpu \
        --cmd_key=accuracy-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-cpu \
        --cmd_key=accuracy-singlestream
```


# Test performance 


## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-cpu \
        --cmd_key=performance-offline
```

## Server

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-cpu \
     --cmd_key=performance-server \
     --env.OMP_NUM_THREADS=8 \
     --env.EXTRA_OPS="--threads 8 --max-batchsize 1 --time 100 --qps 400" 
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-onnx-cpu \
        --cmd_key=performance-singlestream
```
