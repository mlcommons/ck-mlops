# Demo of MLPerf dashboards for ML Systems DSE (Linux and Windows)

* Adaptive CK docker container: [link](https://github.com/octoml/mlops/blob/main/docker/ck-web-service-demo/Dockerfile.ubuntu-20.04)

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
ck build docker:ck-web-service-demo
```

## Run this container
```
ck run docker:ck-web-service-demo
```

## View CK dashboard in your browser

Go to http://localhost:3344/web?action=show&module_uoa=ck-web-service-demo

## Feedback

Contact [Grigori Fursin](https://cKnowledge.io/@gfursin)
