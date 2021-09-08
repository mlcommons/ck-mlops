# Automate MLPerf inference benchmark submission using CK

[![compatibility](https://github.com/ctuning/ck-guide-images/blob/master/ck-compatible.svg)](https://github.com/ctuning/ck)
[![automation](https://github.com/ctuning/ck-guide-images/blob/master/ck-artifact-automated-and-reusable.svg)](https://cTuning.org/ae)


## Prepare

* [Common setup](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/setup/common.md)

Pull extra CK repository with processed components from past MLPerf submission:

```bash
ck pull repo:ck-mlperf-inference
```


## Install CK package to record MLPerf inference results

### New (private) repository for submission

Let's consider that you've created a new (private) Git(Hub) repository 
to save MLPerf results: {{MLPERF_RESULTS_URL}}.

Note that you must have some README.md file in the root directory -
it is used by CK to set up paths.

You can install it via CK to be used with CK automation as follows:


```bash
ck install package --tags=mlperf,inference,results,v1.0 --env.PACKAGE_URL={{MLPERF_RESULTS_URL}}
```

If you have an access to the official (private) v1.1 submission repository, you can install it as follows:
```bash
ck install package --tags=mlperf,inference,results,v1.1-submission-private
```

Alternatively, you can set up a local empty repository for MLPerf results as follows:
```bash
ck install package --tags=mlperf,inference,results,dummy
```

You can find its location as follows:
```bash
ck locate env --tags=mlperf,inference,results
```

You can install this package to another place as follows:
```bash
ck install package --tags=mlperf,inference,results,dummy --install_path={{YOUR PATH}}
```

You can use already existing directory to register in the CK as a place 
to store MLPerf inference results as follows (it should also contain README.md
in the root):

```bash
ck detect soft --tags=mlperf,inference,results --full_path={{PATH TO README.md IN YOUR DIR WITH MLPERF inference results}} --force_version=1.1
```


## Configure your system

CK can run "system" scripts for a given platform to set up frequency, pin cores, etc.
By default, we use a dummy (empty) script configured as follows:

```bash
ck detect platform.os --platform_init_uoa=generic-linux-dummy
```

You can find and use scripts for existing platforms as follows:
```bash
ck ls platform.init | sort
ck detect platform.os --platform_init_uoa={name from the above list}
```

You can create a new one and customize scripts by copying 
and customizing the most related CK components as follows:
```bash
ck cp platform.init:{name from above list} local::{new platform name}
```

You can locate this entry and update scripts as follows:
```bash
cd `ck find platform.init:{new platform name}`
```

It is possible to create a new entry in some public or private CK repo 
instead of the local one as follows:

```bash
ck ls repo | sort
ck cp platform.init:{name from above list} {some repo from the above list}::{new platform name}
```





## Configure your submission


### Set MLPerf inference division
```bash
ck set kernel --var.mlperf_inference_version=1.1
```
 or
```bash
export CK_MLPERF_INFERENCE_VERSION=1.1
```

### Set MLPerf inference division
```bash
ck set kernel --var.mlperf_inference_division=closed
```
 or
```bash
export CK_MLPERF_INFERENCE_DIVISION=closed
```

### Set MLPerf submitter
```bash
ck set kernel --var.mlperf_inference_submitter=OctoML
```
 or
```bash
export CK_MLPERF_INFERENCE_SUBMITTER=OctoML
```


### Set the name of the base system
```bash
ck set kernel --var.mlperf_inference_system=my-machine-ubuntu20.04
```
 or
```bash
export CK_MLPERF_INFERENCE_SYSTEM=my-machine-ubuntu20.04
```

### Add CK entry for the base system

List available systems from past MLPerf inference submissions:
```bash
ck ls bench.mlperf.system:* | sort
```

```bash
ck add bench.mlperf.system:my-machine-ubuntu20.04 (--base={name from above list})
```

For example:
```bash
ck add bench.mlperf.system:my-machine-ubuntu20.04 --base=1-node-8S-CPX-TensorFlow-INT8
```

CK will fill in some keys but you still need to update it further.

Note that above command will create a CK entry with this system
in the "local" repo:
```bash
ck find bench.mlperf.system:my-machine-ubuntu20.04
```

if you want to prepare system description in the public "ck-mlperf-inference" repo
or in your own private submission repo, use the following command:

```bash
ck add {target CK repo name}:bench.mlperf.system:my-machine-ubuntu20.04
```

You can add "user.conf" to the above CK entry to be automatically picked up by CK MLPerf workflows.
You need to add the MLPerf version to this filename: "user.{MLPerf version}.conf", 
i.e. "user.1.1.conf".


## Prepare and test CK workflows for MLPerf image classification

* [Image classification with TVM and ONNX Models](https://github.com/octoml/mlops/tree/main/program/mlperf-inference-bench-image-classification-tvm-onnx-cpu)
* [Image classification with TVM and PyTorch Models](https://github.com/octoml/mlops/tree/main/program/mlperf-inference-bench-image-classification-tvm-pytorch-cpu)
* [Image classification with ONNX and ONNX models](https://github.com/octoml/mlops/tree/main/program/mlperf-inference-bench-image-classification-onnx-cpu)




## Run CK-based MLPerf submission system

CK helps to provide [abstractions at different levels](https://arxiv.org/pdf/2011.01149.pdf) 
to plug in and extend sub-components independently. 
We've developed the ["module:bench.mlperf.inference" workflow](https://github.com/octoml/mlops/blob/main/module/bench.mlperf.inference/module.py#L1230) 
to automatically prepare and test the MLPerf inference submission using above workflows:

### Install Python prerequisites

```bash
ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=offline --mode=prereq
```

### List available flags

```bash
ck run bench.mlperf.inference --help
```

### Test accuracy of a standard model

```bash
ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=offline --mode=accuracy --env.EXTRA_OPS="--count 500"
```

**Note:** This workflow will automatically create the MLPerf directory structure with all the necessary artifacts
and will start populating it with the results! You can locate the place with results as follows:
```bash
ck locate env --tags=mlcommons,results
ls `ck locate env --tags=mlcommons,results`/inference-results

README.md  closed
```

You may still need to check and update files there before the submission.
At the end of running all the necessary steps and tests, you should be able 
to produce a PR from this repository to the official submission repository.


### Customize above run
```bash
ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=offline --mode=performance --loadgen.max-batchsize=1 --loadgen.threads=1 --loadgen.count=5000
```

### Run the compliance tests (TEST01, TEST04, TEST05)

```bash
ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=offline --mode=performance --compliance
```

### Examples of other commands

```bash
ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=offline --mode=performance --loadgen.max-batchsize=1 --loadgen.threads=1 --loadgen.count=5000 --compliance
ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=offline --mode=performance --env.EXTRA_OPS="--count 5000" --compliance
ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --dep_add_tags.model=v1.5-opset-11 --scenario=offline --mode=performance --env.EXTRA_OPS="--count 5000" --compliance

ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=offline --mode=performance --compliance
ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=offline --mode=performance --env.EXTRA_OPS="--count 5000 --time 60 --qps 200 --max-latency 0.1"

ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=offline --mode=accuracy
ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=singlestream --mode=performance --env.EXTRA_OPS="--time 600"
ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=singlestream --mode=performance --env.EXTRA_OPS="--time 600" --compliance

ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=tvm-onnx --model=resnet50 --scenario=offline --mode=accuracy

ck run bench.mlperf.inference --division=closed --submitter=OctoML --system=my-machine-ubuntu20.04 --framework=onnx --model=resnet50 --scenario=offline --mode=accuracy --env.EXTRA_OPS="--count 5000" --experiment_uoa=xyz --experiment_tags=abc
```


### Substitute model

You can try to substitute a standard model with the external one 
(provided that inputs and outputs are the same) using the following environment variable:
```bash
export ML_MODEL_FILEPATH_EXTERNAL={path to some model}
```


## Finalize submission

### Truncate accuracy logs
```bash
ck run program:mlperf-inference-submission --cmd_key=truncate_accuracy_log --env.CK_MLPERF_SUBMITTER=OctoML
```

### Clean backup and truncate accuracy log
```bash
ck run program:mlperf-inference-submission --cmd_key=clean_truncate_accuracy_log --env.CK_MLPERF_SUBMITTER=OctoML
```

### Run submission checker
```bash
ck run program:mlperf-inference-submission --cmd_key=check
```

### Zip results

```bash
ck zip bench.mlperf.inference
```


# Maintainers

* [OctoML.ai](https://OctoML.ai)
* [cTuning foundation](https://cTuning.org)

*Contact: grigori@octoml.ai*
