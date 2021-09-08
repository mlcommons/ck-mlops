# Process MLPerf inference results into CK database format

* Supported host OS to process results: Linux, Windows, MacOS

## Install CK automation for the Python virtual environment

Install CK as described [here](https://github.com/ctuning/ck#installation).

Prepare virtual CK environment:

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

*Note that you can skip the above step and register your own local directory with your results as follows:*
```bash
ck detect soft:mlperf.inference.results  --full_path={FULL PATH TO YOUR DIRECTORY WITH MLPERF RESULTS}/README.md --force_version={SOME VERSION}
```

## Import results into CK format

Create a scratch CK repository to record results (unless you want to record them to the shared "ck-mlperf-inference" repo:
```bash
ck add repo:ck-mlperf-inference-1.1-dse --quiet
```

Import results to this repository:

```bash
ck import bench.mlperf.inference --target_repo=ck-mlperf-inference-1.1-dse
```

Note that we do not yet have a smart way to update results in the repository and they will be appended each time you run the above command.
You may want to clean your results before running this command again:
```bash
ck rm ck-mlperf-inference-1.1-dse:result:* -f
```

## Display all results locally

```bash
ck display dashboard --template=result --cfg=mlperf.inference.all
```

You can customize URL to show results from a given repo (ck_repo) and for a given scenario as follows:

* http://localhost:3344/?template=result&cfg=mlperf.inference.all&cfg_id=mlperf-inference-all-image-classification-edge-singlestream&repo_uoa=ck-mlperf-inference-1.1-dse
* http://localhost:3344/?template=result&cfg=mlperf.inference.all&cfg_id=mlperf-inference-all-image-classification-edge-offline&repo_uoa=ck-mlperf-inference-1.1-dse

You can also specify a given MLPerf scenario and a repository with results from the command line with starting a dashboard (CK version > 2.5.8):

```bash
ck display dashboard --template=result --cfg=mlperf.inference.all --cfg_id=mlperf-inference-all-image-classification-edge-singlestream --repo_uoa=ck-mlperf-inference-1.1-dse
```
or
```bash
ck display dashboard --template=result --cfg=mlperf.inference.all --extra_url="cfg_id=mlperf-inference-all-image-classification-edge-singlestream&repo_uoa=ck-mlperf-inference-1.1-dse"
```

## Display results at cKnowledge.io

* [List dashboards](https://cknowledge.io/?q=%22mlperf-inference-all-*%22)

## Process results on a Pareto frontier

```bash
ck filter ck-mlperf-inference-1.1-dse:bench.mlperf.inference:mlperf-inference-all-image-classification-edge-singlestream-pareto 
ck filter ck-mlperf-inference-1.1-dse:bench.mlperf.inference:mlperf-inference-all-*-pareto 
```

You can remove "ck-mlperf-inference-1.1-dse:" from above commands to process results in all repositories.


# Maintainers

* [cTuning foundation](https://cTuning.org)
* [OctoML.ai](https://OctoML.ai)

*Contact: grigori@octoml.ai*
