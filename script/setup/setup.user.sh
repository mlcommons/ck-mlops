#!/bin/bash


#-----------------------------------------------------------------------------#
# Step 0. Perform basic CK setup and install implicit Python dependencies.
#-----------------------------------------------------------------------------#
echo "## added by $0 :" >> ~/.bashrc
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
export PATH=$HOME/.local/bin:$PATH
export CK_CC=gcc
export CK_PYTHON=/usr/bin/python3
export CK_PYTHON_BIN=/usr/bin/python3

# Install implicit Python dependencies (for Model Optimizer and LoadGen).
${CK_PYTHON} -m pip install ck --user && ck version
${CK_PYTHON} -m pip install --ignore-installed pip setuptools --user
${CK_PYTHON} -m pip install --user \
  nibabel pillow progress py-cpuinfo pyyaml shapely sklearn tqdm xmltodict yamlloader

# Pull CK repositories (including ck-mlperf, ck-env, ck-autotuning, ck-tensorflow, ck-docker).
ck pull repo --url=git@github.com:dividiti/ck-openvino

# Use generic Linux settings with dummy frequency setting scripts.
ck detect platform.os --platform_init_uoa=generic-linux-dummy
# Detect GCC (C/C++ compiler).
ck detect soft:compiler.gcc --full_path=`which ${CK_CC}` --quiet
# Detect Python.
ck detect soft:compiler.python --full_path=`which ${CK_PYTHON}` --quiet
# Detect CMake (build tool).
ck detect soft --tags=cmake --full_path=`which cmake` --quiet
ck show env --tags=64bits

#-----------------------------------------------------------------------------#
# Step 1. Install explicit Python dependencies (for Model Optimizer and LoadGen).
#-----------------------------------------------------------------------------#
# OpenVINO pre-release strictly requires TensorFlow < 2.0 and NetworkX < 2.4.
ck install package --tags=lib,python-package,tensorflow --force_version=1.15.2
ck install package --tags=lib,python-package,networkx --force_version=2.3.0
ck install package --tags=lib,python-package,defusedxml
ck install package --tags=lib,python-package,cython
ck install package --tags=lib,python-package,numpy
# test-generator is an implicit dependency of Model Optimizer (not in requirements.txt).
ck install package --tags=lib,python-package,test-generator
# Abseil is a LoadGen dependency.
ck install package --tags=lib,python-package,absl
# Install "headless" OpenCV (which doesn't need libsm6, libxext6, libxrender-dev).
ck install package --tags=lib,python-package,cv2,opencv-python-headless


#-----------------------------------------------------------------------------#
# Step 2. Install C++ dependencies (for Inference Engine and MLPerf program).
#-----------------------------------------------------------------------------#
ck install package --tags=lib,opencv,v3.4.10
#ck install package --tags=lib,boost,v1.67.0,without-python --no_tags=min-for-caffe
ck install package --tags=lib,boost,v1.67.0 --no_tags=min-for-caffe
# Install LoadGen from a branch reconstructed according to Intel's README.
ck install package --tags=mlperf,inference,source,dividiti.v0.5-intel
ck install package --tags=lib,loadgen,static


#-----------------------------------------------------------------------------#
# Step 3. Install the OpenVINO "pre-release" used for MLPerf Inference v0.5.
#-----------------------------------------------------------------------------#
ck install package --tags=lib,openvino,pre-release
# # FIXME: Make conditional on Ubuntu 18.04?
# cd `ck locate env --tags=lib,openvino,pre-release` \
# && cd openvino/inference-engine/bin/intel64/Release/lib/python_api/ \
# && mv python3.6 python3

#-
#- #-----------------------------------------------------------------------------#
#- # Step 4. Install the first 500 images of the ImageNet 2012 validation dataset
#- # to use as the calibration dataset for image classification models.
#- #-----------------------------------------------------------------------------#
#- RUN ck install package --tags=dataset,imagenet,cal,all.500
#-
#-
#- #-----------------------------------------------------------------------------#
#- # Step 5. Install the official ResNet model for MLPerf Inference v0.5
#- # and convert it into the OpenVINO format.
#- #-----------------------------------------------------------------------------#
#- RUN ck install package --tags=model,tf,mlperf,resnet --no_tags=ssd
#- RUN ck install package --tags=model,openvino,resnet50
#- #-----------------------------------------------------------------------------#
#-
#-
#- #-----------------------------------------------------------------------------#
#- # Step 6. Install the official MobileNet model for MLPerf Inference v0.5
#- # and convert it into the OpenVINO format.
#- #-----------------------------------------------------------------------------#
#- RUN ck install package --tags=model,tf,mlperf,mobilenet-v1-1.0-224,non-quantized
#- RUN ck install package --tags=model,openvino,mobilenet
#- #-----------------------------------------------------------------------------#
#-


#-----------------------------------------------------------------------------#
# Step 7. Install the official SSD-MobileNet model for MLPerf Inference v0.5
# and convert it into the OpenVINO format.
#-----------------------------------------------------------------------------#
ck install package --tags=model,tf,ssd-mobilenet,quantized,for.openvino
ck install package --tags=model,openvino,ssd-mobilenet


#-----------------------------------------------------------------------------#
# Step 8. Install the COCO 2017 validation dataset (5,000 images).
#-----------------------------------------------------------------------------#
echo | ck install package --tags=object-detection,dataset,coco.2017,val,original,full \
    && ck virtual env --tags=object-detection,dataset,coco.2017,val,original,full \
                      --shell_cmd='rm $CK_ENV_DATASET_COCO_LABELS_DIR/*train2017.json'
# Install Python COCO API.
ck install package --tags=lib,python-package,matplotlib
ck install package --tags=tool,coco,api


#-----------------------------------------------------------------------------#
# Run the OpenVINO program that Intel prepared for MLPerf Inference v0.5
# with the quantized SSD-MobileNet model
# on the first 50 images of the COCO 2017 validation dataset
# using all (virtual) CPU cores.
#-----------------------------------------------------------------------------#
export NPROCS=`grep -c processor /proc/cpuinfo` \
&& ck compile program:mlperf-inference-v0.5 \
&& ck run program:mlperf-inference-v0.5 --skip_print_timers \
   --cmd_key=object-detection --env.CK_OPENVINO_MODEL_NAME=ssd-mobilenet \
   --env.CK_LOADGEN_SCENARIO=Offline --env.CK_LOADGEN_MODE=Accuracy --env.CK_LOADGEN_DATASET_SIZE=50 \
   --env.CK_OPENVINO_NTHREADS=$NPROCS --env.CK_OPENVINO_NSTREAMS=$NPROCS --env.CK_OPENVINO_NIREQ=$NPROCS \
&& cat `ck find program:mlperf-inference-v0.5`/tmp/accuracy.txt
