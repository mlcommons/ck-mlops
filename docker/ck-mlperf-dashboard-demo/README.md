# Demo of MLPerf dashboards for ML Systems DSE (Linux and Windows)

## Install CK
```
python3 -m pip install ck
```

## Pull this repository via CK
```
ck pull repo:octoml@mlops
```

## Build this container
```
ck build docker:ck-mlperf-dashboard-demo
```

Note that it will build and run several MLPerf&trade; benchmarks while recording results
to the CK 'experiment' entries to be used in the CK dashboard.

## Run this container
```
ck run docker:ck-mlperf-dashboard-demo
```

## View CK dashboard in your browser

Go to http://localhost:3355/?template=dashboard&scenario=mlperf.mobilenets

## Feedback

Contact [Grigori Fursin](https://cKnowledge.io/@gfursin)
