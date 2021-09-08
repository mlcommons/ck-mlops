# MLPerf inference benchmark workflow

* Automation: [CK](https://github.com/ctuning/ck)
* Task: image classification
* Dataset: ImageNet
* Framework: [TVM](https://github.com/apache/tvm)
* Models: TFLite format
* Target device: CPU

# Preparation

* System prerequisites
  - [x8664; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/x8664-ubuntu.md)
  - [Raspberry Pi 4; Arm64; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/rpi4-ubuntu.md)
  - [Nvidia Jetson Nano; Arm64; Ubuntu 18.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/nvidia-jetson-nano.md)

* [Common setup](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/common.md)
* [Framework installation (TFLite - to load native models)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-tflite.md)
* [Framework installation (TVM)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-tvm.md)

## Dataset

* [Installation](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/datasets/imagenet2012.md)

## Models

For now only non-quantized FP32 models with input 224x224 are supported via TVM backend in MLPerf.

* EfficientNet (quantized/non-quantized): [TensorFlow and TFLite](https://github.com/ctuning/ck-mlops/tree/main/package/model-tflite-mlperf-efficientnet-lite/.cm/meta.json)
* MobileNet-v3 (quantized/non-quantized): [TensorFlow and TFLite](https://github.com/ctuning/ck-mlops/tree/main/package/model-tf-and-tflite-mlperf-mobilenet-v3/.cm/meta.json)
* MobileNet-v2 (quantized): [TensorFlow and TFLite](https://github.com/ctuning/ck-mlops/tree/main/package/model-tf-and-tflite-mlperf-mobilenet-v2-quant/.cm/meta.json)
* MobileNet-v2 (non-quantized): [TensorFlow and TFLite](https://github.com/ctuning/ck-mlops/tree/main/package/model-tf-and-tflite-mlperf-mobilenet-v2/.cm/meta.json)
* MobileNet-v1 (quantized/non-quantized): [TensorFlow and TFLite](https://github.com/ctuning/ck-mlops/tree/main/package/model-tf-and-tflite-mlperf-mobilenet-v1-20180802/.cm/meta.json)


## Python prerequisites

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-tflite-cpu \
        --cmd_key=install-python-requirements
```

# Test accuracy

## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-tflite-cpu \
        --cmd_key=accuracy-offline
```

Customize it:
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-tflite-cpu \
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
time ck run program:mlperf-inference-bench-image-classification-tvm-tflite-cpu \
     --cmd_key=accuracy-server \
     --env.OMP_NUM_THREADS=8 \
     --env.EXTRA_OPS="--threads 8 --max-batchsize 1 --time 100 --qps 500" 
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-tflite-cpu \
        --cmd_key=accuracy-singlestream
```


# Test performance 


## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-image-classification-tvm-tflite-cpu \
        --cmd_key=performance-offline
```

## Server

```bash
time ck run program:mlperf-inference-bench-image-classification-tvm-tflite-cpu \
     --cmd_key=performance-server \
     --env.OMP_NUM_THREADS=8 \
     --env.EXTRA_OPS="--threads 8 --max-batchsize 1 --time 100 --qps 500" 
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-image-classification-tvm-tflite-cpu \
        --cmd_key=performance-singlestream
```
