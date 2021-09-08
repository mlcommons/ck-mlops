# Install CK

[Guide](https://github.com/ctuning/ck#installation)

```bash
python3 -m pip install ck
```

# Pull CK repo with MLPerf Docker images

```bash
ck pull repo:mlcommons@ck-mlops
```

# Update CK and repos

If you have CK and CK repos already installed, you can updated them as follows:
```bash
python3 -m pip install ck -U
ck pull all
```

# MLPerf image classification with TVM

## Build Docker image

```bash
ck build docker:ck-mlperf-inference-dev-image-classification-onnx-tvm
```

See available Docker images [here](https://github.com/mlcommons/ck-mlops/tree/main/docker/ck-mlperf-inference-dev-image-classification-onnx-tvm).

Note that MLPerf benchmark fails on CentOS-8.

## Run Docker image in benchmarking mode
```bash
ck run docker:ck-mlperf-inference-dev-image-classification-onnx-tvm
```

## Run Docker image in interactive mode
```bash
ck run docker:ck-mlperf-inference-dev-image-classification-onnx-tvm --bash

```

# MLPerf object classification with TVM

## Build Docker image

```bash
ck build docker:ck-mlperf-inference-dev-object-detection-onnx-tvm
```

See available Docker images [here](https://github.com/mlcommons/ck-mlops/tree/main/docker/ck-mlperf-inference-dev-object-detection-onnx-tvm).

## Run Docker image in benchmarking mode
```bash
ck run docker:ck-mlperf-inference-dev-object-detection-onnx-tvm
```

## Run Docker image in interactive mode
```bash
ck run docker:ck-mlperf-inference-dev-object-detection-onnx-tvm --bash

```

