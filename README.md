# CK repository for AI and ML systems

[![compatibility](https://github.com/ctuning/ck-guide-images/blob/master/ck-compatible.svg)](https://github.com/ctuning/ck)
[![automation](https://github.com/ctuning/ck-guide-images/blob/master/ck-artifact-automated-and-reusable.svg)](https://cTuning.org/ae)

Linux/MacOS: [![Travis Build Status](https://travis-ci.org/ctuning/ai.svg)](https://travis-ci.org/ctuning/ai)
Windows: [![Windows Build status](https://ci.appveyor.com/api/projects/status/4ry307jh6tks9dg9?svg=true)](https://ci.appveyor.com/project/gfursin/ai)


*There are numerous CK components spread across numerous GitHub repositories. 
Based on the feedback from the community, we have created this repository 
to collect all main CK components related to AI and ML Systems in one place. 
These components are also uploaded to the cKnowledge.io platform 
to ensure the stability of public CK workflows!*

A collection of portable workflows, automation actions and reusable artifacts for AI and ML systems in the [CK format](https://arxiv.org/pdf/2011.01149.pdf):

* CK modules with automation actions: [[dev](https://github.com/ctuning/ai/tree/main/module)] [[stable](https://github.com/ctuning/ck/tree/master/ck/repo/module)]
* CK program workflows: [[dev](https://github.com/ctuning/ai/tree/main/program)] [[CK platform]( https://cKnowledge.io/programs )]
* CK meta packages: [[dev](https://github.com/ctuning/ai/tree/main/package)] [[CK platform]( https://cKnowledge.io/packages )]
* CK software detection: [[dev](https://github.com/ctuning/ai/tree/main/soft)] [[CK platform]( https://cKnowledge.io/soft )]
* CK datasets: [[dev](https://github.com/ctuning/ai/tree/main/dataset)] [[CK platform]( https://cKnowledge.io/c/dataset )]
* CK adaptive containers: [[dev](https://github.com/ctuning/ai/tree/main/docker)] [[CK platform]( https://cKnowledge.io/c/docker )]
* CK OS: [[dev](https://github.com/ctuning/ai/tree/main/os)] [[CK platform]( https://cKnowledge.io/c/os )]
* CK MLPerf system descriptions: [[dev](https://github.com/ctuning/ai/tree/main/sut)] [[CK platform]( https://cKnowledge.io/c/sut )]
* CK MLPerf benchmark CMD generators: [[dev](https://github.com/ctuning/ai/tree/main/cmdgen)] [[CK platform]( https://cKnowledge.io/c/cmdgen )]

All CK components are available at the [CK portal](https://cKnowledge.io) similar to PyPI.
Feel free to discuss them with the [CK community](https://cKnowledge.io/engage).

# Docs

* CK automation framework: 
  [[GitHub]( https://github.com/ctuning/ck )] 
  [[Online docs](https://ck.readthedocs.io)] 
  [[Overview](https://arxiv.org/pdf/2011.01149.pdf)]

# Usage

## Without Docker

Install the CK framework as described [here](https://ck.readthedocs.io/en/latest/src/installation.html).

Pull this repository:
```bash
ck pull repo:ai
```
Test the installation using the simple image corner detection program:

```bash
ck ls program:*susan*

ck search dataset --tags=jpeg

ck compile program:cbench-automotive-susan2 --speed

ck run program:cbench-automotive-susan2 --cmd_key=corners --repeat=1 --env.MY_ENV=123 --env.TEST=xyz

# view output
ls `ck find program:cbench-automotive-susan2`/tmp/output.pgm
```

Try [portable AI/ML workflows](https://cKnowledge.io/solutions), [program pipelines](https://cKnowledge.io/programs)
and [adaptive CK containers](https://cKnowledge.io/c/docker).
*Note that you do not need to pull other repositories anymore
 since all the components are aggregated here.*

Check [public dashboards](https://cKnowledge.io/reproduced-results) with reproduced results from [research papers](https://cKnowledge.io/reproduced-papers).

See real use cases from the community: [MLPerf, Arm, General Motors, IBM, Raspberry Pi foundation, ACM, dividiti and others](https://cknowledge.org/partners.html).

Read about the [CK concept and format](https://arxiv.org/abs/2011.01149).

## With Docker

We have prepared a CK container with all CK components from this repository: 
[[Docker](https://hub.docker.com/r/ctuning/ck-ai)], [[CK meta](https://github.com/ctuning/ai/tree/main/docker/ck-ai)]

You can start it as follows:

```bash
docker run --rm -it ctuning/ck-ai:ubuntu-20.04
```

You can then prepare and run these [portable AI/ML workflows](https://cKnowledge.io/solutions) 
and [program pipelines](https://cKnowledge.io/programs).


# License

BSD 3-clause. We are discussing the possibility to relicense the CK framework and components to Apache 2.0.

# Contributions

Please contribute as described [here](https://ck.readthedocs.io/en/latest/src/how-to-contribute.html)
and submit your PRs [here](https://github.com/ctuning/ai/pulls).

# Acknowledgments

We would like to thank all [collaborators](https://cKnowledge.org/partners.html) for their support, fruitful discussions, 
and useful feedback! See more acknowledgments in the [CK journal article](https://arxiv.org/abs/2011.01149).


# Contacts

Don't hesitate to get in touch with the [CK community](https://cknowledge.org/contacts.html) 
if you have questions or comments.
