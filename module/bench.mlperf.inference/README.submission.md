# MLPerf inference benchmark automation

[![compatibility](https://github.com/ctuning/ck-guide-images/blob/master/ck-compatible.svg)](https://github.com/ctuning/ck)
[![automation](https://github.com/ctuning/ck-guide-images/blob/master/ck-artifact-automated-and-reusable.svg)](https://cTuning.org/ae)

## Install CK

```bash
$ python3 -m pip install ck -U

```
or
```bash
$ python3 -m pip install ck -U --user
```

```bash

$ ck

CK version: 2.5.7

Python executable used by CK: /usr/bin/python3

Python version used by CK: 3.6.9 (default, Jan 26 2021, 15:33:00)
   [GCC 8.4.0]

Path to the CK kernel:    /home/gfursin/.local/lib/python3.6/site-packages/ck/kernel.py
Path to the default repo: /home/gfursin/.local/lib/python3.6/site-packages/ck/repo
Path to the local repo:   /mnt/CK/local
Path to CK repositories:  /mnt/CK

Documentation:        https://github.com/ctuning/ck/wiki
CK Google group:      https://bit.ly/ck-google-group
CK Slack channel:     https://cKnowledge.org/join-slack
Stable CK components: https://cKnowledge.io
```

Follow this [guide](https://github.com/ctuning/ck#installation) for more details.



## Automate MLPerf inference submission

Follow [this guide](README.submission.md)

## Process and visualize MLPerf results

Follow [this guide](README.results.md)




## Install CK automation for Python virtual environment

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
ck set kernel var.mlperf_inference_version=1.0
```
 or
```bash
export CK_MLPERF_INFERENCE_VERSION=1.0
```

### Set MLPerf inference division
```bash
ck set kernel var.mlperf_inference_division=closed
```
 or
```bash
export CK_MLPERF_INFERENCE_DIVISION=closed
```

### Set MLPerf submitter
```bash
ck set kernel var.mlperf_submitter=OctoML
```
 or
```bash
export CK_MLPERF_SUBMITTER=OctoML
```


### Set the name of the base system
```bash
ck set kernel.var.mlperf_system_base=rpi4-ubuntu20.04
```
 or
```bash
export CK_MLPERF_SYSTEM_BASE=rpi4-ubuntu20.04
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
