# News 
* **20210525: This container was tested, fixed and improved by [Grigori Fursin](https://cKnowledge.io/@gfursin) to support the latest CK version! 
  See [octoml@mlops repo](https://github.com/octoml/mlops) and [MLPerf automation docs](https://github.com/ctuning/ck/blob/master/docs/mlperf-automation/README.md) for more details.**

# MLPerf Inference v0.7 - OpenVINO

Adaptive CK containers with [automated CK workflows](https://github.com/ctuning/ck) for OpenVINO workoads.

| `CK_TAG` (`Dockerfile`'s extension)  | Python | GCC   | Comments |
|-|-|-|-|
| `ubuntu-20.04` | 3.8.2 | 9.3.0 ||

<a name="setup_ck"></a>
## Set up Collective Knowledge

You will need to install [Collective Knowledge](httpы://cknowledge.org) to build images and save benchmarking results.
Please follow the [CK installation instructions](https://github.com/ctuning/ck#installation) and then pull the ck-mlperf repository:

```bash
$ ck pull repo:ck-ml
```

**NB:** Refresh all CK repositories after any updates (e.g. bug fixes):
```bash
$ ck pull all
```

## Build (Linux or Windows)

To build an image e.g. from `Dockerfile.ubuntu-20.04`:
```bash
$ ck build docker:mlperf-inference-v0.5.openvino --tag=ubuntu-20.04
```

## Run the default command (Linux or Windows)

To run the default command of an image e.g. built from `Dockerfile.ubuntu-20.04`:
```bash
$ ck run docker:mlperf-inference-v0.5.openvino --tag=ubuntu-20.04
...
Accumulating evaluation results...
DONE (t=0.22s).
 Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = 0.244
 Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ] = 0.380
 Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ] = 0.280
 Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = 0.032
 Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = 0.193
 Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = 0.576
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ] = 0.225
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ] = 0.264
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = 0.266
 Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = 0.037
 Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = 0.198
 Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = 0.619
mAP=24.354%
```
