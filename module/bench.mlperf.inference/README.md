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

## Install CK automation for Python virtual environment

```bash
ck pull repo:octoml@venv

ck create venv:mlperf --template=generic

ck activate venv:mlperf
```

## Pull already processed results
```bash
ck pull repo:ck-mlperf-inference
```

## Install CK packages with MLPerf inference results

```bash
ck install package --tags=mlperf,inference,results,v1.0
ck install package --tags=mlperf,inference,results,v0.7
ck install package --tags=mlperf,inference,results,v0.5
```

## Import results into CK format

```bash
ck import bench.mlperf.inference --target_repo=ck-mlperf-inference
```

## Display results locally

```bash
ck display dashboard --template=result --cfg=mlperf.inference.all
```

## Process results on a Pareto frontier

```bash
ck filter bench.mlperf.inference:mlperf-inference-all-image-classification-edge-singlestream-pareto 
ck filter bench.mlperf.inference:mlperf-inference-all-*-pareto 
```


# Maintainers

* [cTuning foundation](https://cTuning.org)
* [OctoML.ai](https://OctoML.ai)

*Contact: grigori@octoml.ai*
