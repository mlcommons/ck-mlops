***April 2022: We've started prototyping the new [CK2 toolkit](https://github.com/mlcommons/ck/tree/master/ck2) 
   based on your feedback and combined with our practical experience 
   [reproducing 150+ ML and Systems papers and validating them in the real world](https://www.youtube.com/watch?v=7zpeIVwICa4).
   Please [get in touch](https://github.com/mlcommons/ck/tree/master/ck2#contacts) if you are interested to participate in this community effort!***

# CK repository with automation workflows for MLPerf and MLOps

[![compatibility](https://github.com/ctuning/ck-guide-images/blob/master/ck-compatible.svg)](https://github.com/mlcommons/ck)
[![automation](https://github.com/ctuning/ck-guide-images/blob/master/ck-artifact-automated-and-reusable.svg)](https://cTuning.org/ae)
[![Windows Build status](https://ci.appveyor.com/api/projects/status/sgmfvegn78svfss0?svg=true)](https://ci.appveyor.com/project/gfursin/ck-mlops)

## CK compatibility

This repository is compatible with the [MLCommons CK framework](https://github.com/mlcommons/ck) **v2.5.8** (Apache 2.0 license):

## Documentation

* [CK-powered MLPerf&trade; benchmark automation and design space exploration](https://github.com/mlcommons/ck/blob/master/docs/mlperf-automation/README.md)
* [CK-powered MLPerf&trade; inference submission automation](https://github.com/mlcommons/ck-mlops/tree/main/module/bench.mlperf.inference)

## Overview

This repository contains a collection of **stable** [CK components](https://arxiv.org/pdf/2011.01149.pdf) 
(automation recipes and workflows) to automate benchmarking, optimization and deployment of ML Systems 
across diverse platforms, environments, frameworks, models and data sets: 

* CK automation recipes for MLOps: [[inside CK framework](https://github.com/mlcommons/ck/tree/master/ck/repo/module)] [[in this repo](https://github.com/mlcommons/ck-mlops/tree/master/module)]
* CK portable program workflows: [[list]( https://github.com/mlcommons/ck-mlops/tree/master/program )]
* CK portable meta packages: [[list]( https://github.com/mlcommons/ck-mlops/tree/master/package )]
* CK environment detection (software, models, data sets): [[list]( https://github.com/mlcommons/ck-mlops/tree/master/soft )]
* CK OS descriptions: [[list]( https://github.com/mlcommons/ck-mlops/tree/master/os )]
* CK adaptive containers: [[list]( https://github.com/mlcommons/ck-mlops/tree/master/docker )]

## Current projects
* Developing a platform to automate SW/HW co-design for ML Systems across diverse models, data sets, frameworks and platforms based on user constraints in terms of speed, accuracy, energy and costs: [OctoML.ai](https://OctoML.ai) & [cKnowledge.io](https://cKnowledge.io)
* [Automating MLPerf(tm) inference benchmark and packing ML models, data sets and frameworks as CK components with a unified API and meta description](https://github.com/mlcommons/ck/blob/master/docs/mlperf-automation/README.md)
* Providing a common format to share artifacts at ML, systems and other conferences: [video](https://youtu.be/DIkZxraTmGM), [Artifact Evaluation](https://cTuning.org/ae)
* Redesigning CK together with the community based on user feedback

## Use cases
* Real-world use cases from our partners: [overview](https://cKnowledge.org/partners.html)

# Motivation

* [ACM TechTalk on YouTube](https://www.youtube.com/watch?=7zpeIVwICa4)
* [White paper](https://arxiv.org/pdf/2006.07161.pdf) and [extended journal article](https://arxiv.org/pdf/2011.01149.pdf)

# Coordinator

* [Grigori Fursin (OctoML/cTuning foundation)](https://fursin.net)

# Problems

Don't hesitate to report issues or submit feature requests [here](https://github.com/mlcommons/ck-mlops/issues).

# Public discussions

Contact [Grigori Fursin](mailto:grigori@octoml.ai) to join our MLCommons Design Space Exploration Workgroup (subgroup of Best Practices)!
