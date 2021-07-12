# Process MLPerf inference results into CK database format

## Install CK automation for the Python virtual environment

```bash
ck pull repo:octoml@venv

ck create venv:mlperf --template=generic

ck activate venv:mlperf
```

## Pull CK repo with MLOps automation recipes
```bash
ck pull repo:octoml@mlops
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

## Display results at cKnowledge.io

* [List dashboards](https://cknowledge.io/?q=%22mlperf-inference-all-*%22)

## Process results on a Pareto frontier

```bash
ck filter bench.mlperf.inference:mlperf-inference-all-image-classification-edge-singlestream-pareto 
ck filter bench.mlperf.inference:mlperf-inference-all-*-pareto 
```


# Maintainers

* [cTuning foundation](https://cTuning.org)
* [OctoML.ai](https://OctoML.ai)

*Contact: grigori@octoml.ai*
