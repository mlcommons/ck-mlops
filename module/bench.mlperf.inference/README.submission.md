# Automate MLPerf inference benchmark submission using CK

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






## Install CK automation for the Python virtual environment

Create virtual environment for MLPerf
```bash
ck pull repo:octoml@venv

ck create venv:mlperf --template=generic

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



## Install CK package with MLPerf inference results

### New (private) repository for submission

Let's consider that you've created a new (private) Git(Hub) repository 
to save MLPerf results: {{MLPERF_RESULTS_URL}}.

Note that you must have some README.md file in the root directory -
it is used by CK to set up paths.

You can install it via CK to be used with CK automation as follows:


```bash
ck install package --tags=mlperf,inference,results,r1.1 --env.PACKAGE_URL={{MLPERF_RESULTS_URL}}
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







## Run MLPerf inference benchmark

```bash
ck run bench.mlperf.inference
```






# Maintainers

* [cTuning foundation](https://cTuning.org)
* [OctoML.ai](https://OctoML.ai)

*Contact: grigori@octoml.ai*
