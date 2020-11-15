# CK repository for AI

[![compatibility](https://github.com/ctuning/ck-guide-images/blob/master/ck-compatible.svg)](https://github.com/ctuning/ck)
[![automation](https://github.com/ctuning/ck-guide-images/blob/master/ck-artifact-automated-and-reusable.svg)](https://cKnowledge.io)

Linux/MacOS: [![Travis Build Status](https://travis-ci.org/ctuning/ai.svg?branch=master)](https://travis-ci.org/ctuning/ai)
Windows: [![Windows Build status](https://ci.appveyor.com/api/projects/status/4ry307jh6tks9dg9?svg=true)](https://ci.appveyor.com/project/gfursin/ai)


A collection of portable AI workflows, automation actions and reusable artifacts in the [CK format](https://github.com/ctuning/ck)
aggregated from the following CK repositories:

* [armnn-mlperf](https://github.com/arm-software/armnn-mlperf)
* [ck-analytics](https://github.com/ctuning/ck-analytics)
* [ck-armnn](https://github.com/ctuning/ck-armnn.git)
* [ck-autotuning](https://github.com/ctuning/ck-autotuning)
* [ck-caffe2](https://github.com/ctuning/ck-caffe2)
* [ck-caffe](git@github.com:dividiti/ck-caffe.git)
* [ck-cntk](https://github.com/ctuning/ck-cntk)
* [ck-coral](https://github.com/ctuning/ck-coral)
* [ck-crowdtuning-platforms](https://github.com/ctuning/ck-crowdtuning-platforms)
* [ck-crowdtuning](https://github.com/ctuning/ck-crowdtuning)
* [ck-dnndk](http://github.com/ctuning/ck-dnndk)
* [ck-docker](https://github.com/ctuning/ck-docker)
* [ck-env](https://github.com/ctuning/ck-env)
* [ck-math](https://github.com/ctuning/ck-math)
* [ck-mlflow](https://github.com/ctuning/ck-mlflow)
* [ck-mlperf](https://github.com/ctuning/ck-mlperf)
* [ck-mvnc](https://github.com/ctuning/ck-mvnc)
* [ck-mxnet](https://github.com/ctuning/ck-mxnet)
* [ck-nntest]( https://github.com/ctuning/ck-nntest )
* [ck-object-detection](https://github.com/ctuning/ck-object-detection)
* [ck-openvino](https://github.com/ctuning/ck-openvino)
* [ck-pytorch](https://github.com/ctuning/ck-pytorch)
* [ck-tbd-suite](https://github.com/ctuning/ck-tbd-suite)
* [ck-tensorflow-codereef](https://github.com/code-reef/ck-tensorflow-codereef)
* [ck-tensorflow](https://github.com/ctuning/ck-tensorflow)
* [ck-tensorrt](http://github.com/ctuning/ck-tensorrt)
* [ck-tiny-dnn](https://github.com/ctuning/ck-tiny-dnn)
* [ck-tvm](https://github.com/ctuning/ck-tvm)
* [ck-web](https://github.com/ctuning/ck-web)
* [ctuning-datasets-min](https://github.com/ctuning/ctuning-datasets-min)
* [ctuning-programs](https://github.com/ctuning/ctuning-programs)

# Important components

* CK modules with automation actions: [[dev](https://github.com/ctuning/ai/tree/main/module)] [[stable](https://github.com/ctuning/ck/tree/master/ck/repo/module)]
* CK program workflows: [[dev](https://github.com/ctuning/ai/tree/main/program)] [[CK platform]( https://cKnowledge.io/programs )]
* CK meta packages: [[dev](https://github.com/ctuning/ai/tree/main/package)] [[CK platform]( https://cKnowledge.io/packages )]
* CK software detection: [[dev](https://github.com/ctuning/ai/tree/main/soft)] [[CK platform]( https://cKnowledge.io/soft )]
* CK datasets: [[dev](https://github.com/ctuning/ai/tree/main/dataset)] [[CK platform]( https://cKnowledge.io/c/dataset )]
* CK adaptive containers: [[dev](https://github.com/ctuning/ai/tree/main/docker)] [[CK platform]( https://cKnowledge.io/c/docker )]
* CK OS: [[dev](https://github.com/ctuning/ai/tree/main/os)] [[CK platform]( https://cKnowledge.io/c/os )]
* CK MLPerf system descriptions: [[dev](https://github.com/ctuning/ai/tree/main/sut)] [[CK platform]( https://cKnowledge.io/c/sut )]
* CK MLPerf benchmark CMD generators: [[dev](https://github.com/ctuning/ai/tree/main/cmdgen)] [[CK platform]( https://cKnowledge.io/c/cmdgen )]

All CK components are available at the [CK portal](https://cKnowledge.io) similar to Pypi.

# Usage

Install the CK framework as described [here](https://ck.readthedocs.io/en/latest/src/installation.html).

Pull this repository:
```bash
ck pull repo:ai
```

Try [portable AI/ML workflows](https://cKnowledge.io/solutions)
or [adaptive CK containers](https://cKnowledge.io/c/docker).
*Note that you do not need to pull other repositories anymore
 since all the components are aggregated here.*

Check [public dashboards](https://cKnowledge.io/reproduced-results) with reproduced results from [research papers](https://cKnowledge.io/reproduced-papers).

Read about [CK concept](https://arxiv.org/abs/2011.01149).

Discuss CK using this [public forum](https://groups.google.com/forum/#!forum/collective-knowledge).

Contribute as described [here](https://ck.readthedocs.io/en/latest/src/how-to-contribute.html)
and submit your PR [here](https://github.com/ctuning/ai/pulls).

Contact [the community](https://cknowledge.org/contacts.html).
