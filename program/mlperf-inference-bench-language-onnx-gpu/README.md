# MLPerf inference benchmark workflow

* Automation: [CK](https://github.com/ctuning/ck)
* Task: language (NLP)
* Dataset: SQuAD v1.1
* Framework: [ONNX runtime](https://github.com/microsoft/onnxruntime)
* Models: ONNX format
* Target device: GPU

# Preparation

* System prerequisites
  - [x8664; Ubuntu 20.04 (system deps)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/platform/x8664-ubuntu.md)

* [Common setup](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/common.md)
* [Framework installation (ONNX GPU)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-onnx.md)
* [Framework installation (PyTorch - for some scripts)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-pytorch.md)
* [Framework installation (TensorFlow - for some scripts)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/framework-tf.md)
* [Framework installation (Transformers)](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/lib-transformers.md)

## Dataset

* [Installation](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/datasets/squad.md)

## Models

```bash
ck install package --tags=ml-model,language,bert-large-squad
```
```

## Python prerequisites

```bash
ck run program:mlperf-inference-bench-language-onnx-gpu \
        --cmd_key=install-python-requirements
```

# Test accuracy

## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-language-onnx-gpu \
        --cmd_key=accuracy-offline
```

Customize it:
```bash
ck run program:mlperf-inference-bench-language-onnx-gpu \
        --cmd_key=accuracy-offline \
        --env.CK_LOADGEN_MAX_EXAMPLES=10

```

## Server

```bash
ck run program:mlperf-inference-bench-language-onnx-gpu \
        --cmd_key=accuracy-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-language-onnx-gpu \
        --cmd_key=accuracy-singlestream
```


# Test performance 


## Offline

Run with default parameters
```bash
ck run program:mlperf-inference-bench-language-onnx-gpu \
        --cmd_key=performance-offline
```

## Server

```bash
ck run program:mlperf-inference-bench-language-onnx-gpu \
        --cmd_key=performance-server
```

## SingleStream

```bash
ck run program:mlperf-inference-bench-language-onnx-gpu \
        --cmd_key=performance-singlestream
```
