# Automate MLPerf inference benchmark submission using CK



## Install CK automation for the Python virtual environment

List available templates:
```bash
ck ls venv.template | sort
```

```bash
ck pull repo:octoml@venv

ck create venv:mlperf --template=mlperf-inference-1.0

ck activate venv:mlperf
```



## Pull CK repo with MLOps automation recipes from OctoML
```bash
ck pull repo:octoml@mlops
```

## Pull already processed MLPerf inference results
```bash
ck pull repo:ck-mlperf-inference
```



## Install CK package with MLPerf inference results (can be private for submission)

```bash
ck install package --tags=mlperf,inference,results
```


## Configure submission

### Set MLPerf inference version
```bash
ck set kernel --var.mlperf_inference_version=1.0
```
 or
```bash
export CK_MLPERF_INFERENCE_VERSION=1.0
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
ck set kernel --var.mlperf_inference_system=rpi4-ubuntu20.04
```
 or
```bash
export CK_MLPERF_INFERENCE_SYSTEM=rpi4-ubuntu20.04
```

### Add CK entry for the base system

List available systems from past MLPerf inference submissions:
```bash
ck ls bench.mlperf.system:*rpi4* | sort
```

```bash
ck add bench.mlperf.system:rpi4-ubuntu20.04 (--base={name from above list})
```

For example:
```bash
ck add bench.mlperf.system:rpi4-ubuntu20.04 --base=rpi4-tflite-v2.2.0-ruy
```

CK will fill in some keys but you still need to update it further.

Note that above command will create a CK entry with this system
in the "local" repo:
```bash
ck find bench.mlperf.system:rpi4-ubuntu20.04
```

if you want to prepare system description in the public "ck-mlperf-inference" repo
or in your own private submission repo, use the following command:

```bash
ck add {target CK repo name}:bench.mlperf.system:rpi4-ubuntu20.04
```











# Maintainers

* [cTuning foundation](https://cTuning.org)
* [OctoML.ai](https://OctoML.ai)

*Contact: grigori@octoml.ai*
