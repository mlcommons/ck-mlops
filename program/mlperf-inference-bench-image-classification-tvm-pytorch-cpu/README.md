# MLPerf inference benchmark workflow

* Automation: [CK](https://github.com/ctuning/ck)
* Task: image classification
* Dataset: ImageNet
* Framework: [TVM with DNNL support](https://github.com/apache/tvm) 
* Models: PyTorch format
* Target device: CPU

# Preparation

* System prerequisites
  - [x8664; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/x8664-ubuntu.md)
  - [Raspberry Pi 4; Arm64; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/rpi4-ubuntu.md)
  - [Nvidia Jetson Nano; Arm64; Ubuntu 18.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/nvidia-jetson-nano.md)

* [Common setup](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/common.md)
* [Framework installation (PyTorch - to load native models)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-pytorch.md)
* [Framework installation (TVM)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-tvm.md)

## Dataset

* [Installation](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/datasets/imagenet2012.md)

## Models

```bash
ck install package --tags=model,image-classification,mlperf,pytorch
```

For now, we support only [resnet50_INT8bit_quantized.pt]( https://github.com/mlcommons/ck-mlops/blob/main/package/ml-model-mlperf-resnet50-pytorch/.cm/meta.json ) model.


## Python prerequisites

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-pytorch-cpu \
        --cmd_key=install-python-requirements
```

# Test accuracy

## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-pytorch-cpu \
        --cmd_key=accuracy-offline
```

Customize it:
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-pytorch-cpu \
        --cmd_key=accuracy-offline \
        --env.MLPERF_TVM_EXECUTOR=graph \
        --env.MLPERF_TVM_TARGET="llvm" \
        --env.OMP_NUM_THREADS=4 \
        --env.EXTRA_OPS="--count 100 --threads 4 --max-batchsize 1"
```

Notes:
* You can delete compiled model using flag ```--env.MLPERF_DELETE_COMPILED_MODEL=YES```
* You can force to use DNNL with a flag ```--env.MLPERF_TVM_USE_DNNL=YES```
* You can use your own compatible model by adding --model flag to EXTRA_OPS: ```--env.EXTRA_OPS="--model {FULL PATH}"```


## Server

```bash
time ck run program:mlperf-inference-bench-image-classification-tvm-pytorch-cpu \
     --cmd_key=accuracy-server \
     --env.OMP_NUM_THREADS=8 \
     --env.EXTRA_OPS="--threads 8 --max-batchsize 1 --time 100 --qps 500" 
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-pytorch-cpu \
        --cmd_key=accuracy-singlestream
```


# Test performance 


## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-pytorch-cpu \
        --cmd_key=performance-offline
```

## Server

```bash
time ck run program:mlperf-inference-bench-image-classification-tvm-pytorch-cpu \
     --cmd_key=performance-server \
     --env.OMP_NUM_THREADS=8 \
     --env.EXTRA_OPS="--threads 8 --max-batchsize 1 --time 100 --qps 500" 
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-pytorch-cpu \
        --cmd_key=performance-singlestream
```
