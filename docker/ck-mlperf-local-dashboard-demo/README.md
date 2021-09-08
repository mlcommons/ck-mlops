# Demo of MLPerf dashboards for ML Systems DSE (Linux and Windows)

This container demonstrates how to run CK experiments and record results 
from the Docker in the local "mlperf-mobilenets" repository on the host machine
to be processed in Jupyter notebooks or visualized using CK dashboards.

## Install CK
```
python3 -m pip install ck
```

## Pull this repository via CK
```
ck pull repo:octoml@mlops
```

## Create local mlperf-mobilenets repo
```
ck add repo:mlperf-mobilenets --quiet
```

## Build this container
```
ck build docker:ck-mlperf-local-dashboard-demo
```

## Run this container

You must run this container using a special script from this directory:
* Linux: [docker-start.sh](docker-start.sh)
* Windows: [docker-start.bat](docker-start.bat)

This script will mount local CK mlperf-mobilenets repo inside Docker
to be able to record experiments there from the Docker container.

This script will call a helper script [docker-helper.sh](docker-helper.sh) 
with benchmarks that you can modify to run different experiments.

## View CK dashboard localy

Run the following command from your host machine to visualize results:
```
ck display dashboard --scenario=mlperf.mobilenets
```

## Feedback

Contact [Grigori Fursin](https://cKnowledge.io/@gfursin)
