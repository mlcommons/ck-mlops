/*
 * Copyright (c) 2016-2018 DeePhi Tech, Inc.
 *
 * All Rights Reserved. No part of this source code may be reproduced
 * or transmitted in any form or by any means without the prior written
 * permission of DeePhi Tech, Inc.
 *
 * Filename: main.cc
 * Version: 2.05
 *
 * Description:
 * Sample source code to illustrate how to deploy ResNet50 neural network
 * on DeePhi DPU platform.
 */
#include <assert.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <unistd.h>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <queue>
#include <string>
#include <vector>

/* header file OpenCV for image processing */
#include <opencv2/opencv.hpp>

/* header file for DNNDK APIs */
#include <dnndk/dnndk.h>

using namespace std;
using namespace cv;

/* 7.71GOP computation for ResNet50 Convolution layers */
#define RESNET50_WORKLOAD_CONV (7.71f)
/* (4/1000)GOP computation for ResNet50 FC layers */
#define RESNET50_WORKLOAD_FC (4.0f / 1000)

/* DPU Kernel Name for ResNet50 CONV & FC layers */
#define KERNEL_CONV "resnet50_0"
#define KERNEL_FC "resnet50_2"

#define CONV_INPUT_NODE "conv1"
#define CONV_OUTPUT_NODE "res5c_branch2c"
#define FC_INPUT_NODE "fc1000"
#define FC_OUTPUT_NODE "fc1000"

string baseImagePath = "/root/samples/common/image500_640_480/";
string kindsPath = baseImagePath + "words.txt";

/**
 * @brief Read CK env vars to override default paths.
 */
void readPathsFromEnv() {
  const char *imagenet_synset_words_txt = getenv("CK_CAFFE_IMAGENET_SYNSET_WORDS_TXT");
  if (imagenet_synset_words_txt)
    kindsPath = string(imagenet_synset_words_txt);

  const char *imagenet_val = getenv("CK_CAFFE_IMAGENET_VAL");
  if (imagenet_val)
    baseImagePath = string(imagenet_val);
}

/**
 * @brief Calculate elapsed wall clock time in microseconds
 * between two gettimeofday timestamps.
 */
long long timeWallclock(struct timeval start, struct timeval stop) {
  long long delta_us = (stop.tv_sec-start.tv_sec)*1000000 + (stop.tv_usec-start.tv_usec);
  return delta_us;
}

/**
 * @brief put image names to a vector
 *
 * @param path - path of the image direcotry
 * @param images - the vector of image name
 *
 * @return none
 */
void ListImages(string const &path, vector<string> &images) {
  images.clear();
  struct dirent *entry;

  /*Check if path is a valid directory path. */
  struct stat s;
  lstat(path.c_str(), &s);
  if (!S_ISDIR(s.st_mode)) {
    fprintf(stderr, "Error: %s is not a valid directory!\n", path.c_str());
    exit(1);
  }

  DIR *dir = opendir(path.c_str());
  if (dir == nullptr) {
    fprintf(stderr, "Error: Open %s path failed.\n", path.c_str());
    exit(1);
  }

  while ((entry = readdir(dir)) != nullptr) {
    if (entry->d_type == DT_REG || entry->d_type == DT_UNKNOWN) {
      string name = entry->d_name;
      string ext = name.substr(name.find_last_of(".") + 1);
      if ((ext == "JPEG") || (ext == "jpeg") || (ext == "JPG") ||
          (ext == "jpg") || (ext == "PNG") || (ext == "png")) {
        images.push_back(name);
      }
    }
  }

  closedir(dir);
}

/**
 * @brief load kinds from file to a vector
 *
 * @param path - path of the kinds file
 * @param kinds - the vector of kinds string
 *
 * @return none
 */
void LoadWords(string const &path, vector<string> &kinds) {
  kinds.clear();
  fstream fkinds(path);
  if (fkinds.fail()) {
    fprintf(stderr, "Error : Open %s failed.\n", path.c_str());
    exit(1);
  }
  string kind;
  while (getline(fkinds, kind)) {
    kinds.push_back(kind);
  }

  fkinds.close();
}

/**
 * @brief calculate softmax
 *
 * @param data - pointer to input buffer
 * @param size - size of input buffer
 * @param result - calculation result
 *
 * @return none
 */
void CPUCalcSoftmax(const float *data, size_t size, float *result) {
  assert(data && result);
  double sum = 0.0f;

  for (size_t i = 0; i < size; i++) {
    result[i] = exp(data[i]);
    sum += result[i];
  }

  for (size_t i = 0; i < size; i++) {
    result[i] /= sum;
  }
}

/**
 * @brief Get top k results according to its probability
 *
 * @param d - pointer to input data
 * @param size - size of input data
 * @param k - calculation result
 * @param vkinds - vector of kinds
 *
 * @return none
 */
void TopK(const float *d, int size, int k, vector<string> &vkind) {
  assert(d && size > 0 && k > 0);
  priority_queue<pair<float, int>> q;

  for (auto i = 0; i < size; ++i) {
    q.push(pair<float, int>(d[i], i));
  }

  for (auto i = 0; i < k; ++i) {
    pair<float, int> ki = q.top();
    printf("top[%d] prob = %-8f  name = %s\n", i, d[ki.second],
           vkind[ki.second].c_str());
    q.pop();
  }
}

/**
 * @brief Compute average pooling on CPU
 *
 * @param conv - pointer to ResNet50 CONV Task
 * @param fc - pointer to ResNet50 FC Task
 *
 * @return none
 */
void CPUCalcAvgPool(DPUTask *conv, DPUTask *fc) {
  assert(conv && fc);

  /* Get output Tensor to the last Node of ResNet50 CONV Task */
  DPUTensor *outTensor = dpuGetOutputTensor(conv, CONV_OUTPUT_NODE);
  /* Get size, height, width and channel of the output Tensor */
  int tensorSize = dpuGetTensorSize(outTensor);
  int outHeight = dpuGetTensorHeight(outTensor);
  int outWidth = dpuGetTensorWidth(outTensor);
  int outChannel = dpuGetTensorChannel(outTensor);

  /* allocate memory buffer */
  float *outBuffer = new float[tensorSize];

  /* Get the input address to the first Node of FC Task */
  int8_t *fcInput = dpuGetInputTensorAddress(fc, FC_INPUT_NODE);

  /* Copy the last Node's output and convert them from IN8 to FP32 format */
  dpuGetOutputTensorInHWCFP32(conv, CONV_OUTPUT_NODE, outBuffer, tensorSize);

  /* Get scale value for the first input Node of FC task */
  float scaleFC = dpuGetInputTensorScale(fc, FC_INPUT_NODE);
  int length = outHeight * outWidth;
  float avg = (float)(length * 1.0f);

  float sum;
  for (int i = 0; i < outChannel; i++) {
    sum = 0.0f;
    for (int j = 0; j < length; j++) {
      sum += outBuffer[outChannel * j + i];
    }
    /* compute average and set into the first input Node of FC Task */
    fcInput[i] = (int8_t)(sum / avg * scaleFC);
  }

  delete[] outBuffer;
}

/**
 * @brief Run CONV Task and FC Task for ResNet50
 *
 * @param taskConv - pointer to ResNet50 CONV Task
 * @param taskFC - pointer to ResNet50 FC Task
 *
 * @return none
 */
void runResnet50(DPUTask *taskConv, DPUTask *taskFC) {
  assert(taskConv && taskFC);
  /* Mean value for ResNet50 specified in Caffe prototxt */
  vector<string> kinds, images;
  /* Load all image names.*/
  ListImages(baseImagePath, images);
  if (images.size() == 0) {
    cerr << "\nError: No images found in " << baseImagePath << endl;
    return;
  }

  /* Load all class descriptions.*/
  LoadWords(kindsPath, kinds);
  if (kinds.size() == 0) {
    cerr << "\nError: No class descriptions found in " << kindsPath << endl;
    return;
  }

  /* Get channel count of the output Tensor for FC Task  */
  int channel = dpuGetOutputTensorChannel(taskFC, FC_OUTPUT_NODE);
  float *softmax = new float[channel];
  float *FCResult = new float[channel];
  for (auto &imageName : images) {
    /* Wallclock timestamps */
    const size_t n = 7;
    struct timeval t[n];

    gettimeofday(&t[0], NULL);

    /* Load image and Set image into CONV Task with mean value */
    cout << "\nLoad image : " << imageName << endl;
    Mat image = imread(baseImagePath + imageName);
    dpuSetInputImage2(taskConv, CONV_INPUT_NODE, image);

    gettimeofday(&t[1], NULL);

    /* Run CONV on DPU */
    dpuRunTask(taskConv);

    gettimeofday(&t[2], NULL);

    /* Run AVGPOOL on CPU (not supported by DPU@Zynq7020) */
    CPUCalcAvgPool(taskConv, taskFC);

    gettimeofday(&t[3], NULL);

    /* Run FC on DPU */
    dpuRunTask(taskFC);

    gettimeofday(&t[4], NULL);

    /* Get FC result and convert from INT8 to FP32 */
    dpuGetOutputTensorInHWCFP32(taskFC, FC_OUTPUT_NODE, FCResult, channel);

    gettimeofday(&t[5], NULL);

    /* Run SOFTMAX on CPU */
    CPUCalcSoftmax(FCResult, channel, softmax);

    gettimeofday(&t[6], NULL);

    /* Show TOP5 classification results */
    TopK(softmax, channel, 5, kinds);

    /* Output DPU and WALLCLOCK profiling times in microseconds */
    cout << "Profiling info:\n";
    long long timeProf;
    /* Output DPU execution time of CONV Task */
    timeProf = dpuGetTaskProfile(taskConv);
    cout << "  DPU CONV Execution time: " << (timeProf * 1.0f) << "us\n";
    float convProf = (RESNET50_WORKLOAD_CONV / timeProf) * 1000000.0f;
    cout << "  DPU CONV Performance: " << convProf << "GOPS\n";
    /* Output DPU execution time of FC Task */
    timeProf = dpuGetTaskProfile(taskFC);
    cout << "  DPU FC Execution time: " << (timeProf * 1.0f) << "us\n";
    float fcProf = (RESNET50_WORKLOAD_FC / timeProf) * 1000000.0f;
    cout << "  DPU FC Performance: " << fcProf << "GOPS\n";
    /* Output wall clock times (in microseconds) */
    cout << "  WALLCLOCK01 LOAD Execution time: "       << timeWallclock(t[0], t[1]) << "us\n";
    cout << "  WALLCLOCK12 CONV Execution time: "       << timeWallclock(t[1], t[2]) << "us\n";
    cout << "  WALLCLOCK23 AVGPOOL Execution time: "    << timeWallclock(t[2], t[3]) << "us\n";
    cout << "  WALLCLOCK34 FC Execution time: "         << timeWallclock(t[3], t[4]) << "us\n";
    cout << "  WALLCLOCK45 INT8->FP32 Execution time: " << timeWallclock(t[4], t[5]) << "us\n";
    cout << "  WALLCLOCK56 SOFTMAX Execution time: "    << timeWallclock(t[5], t[6]) << "us\n";
    cout << "  WALLCLOCK16 COMPUTE Execution time: "    << timeWallclock(t[1], t[6]) << "us\n";
    cout << "  WALLCLOCK06 TOTAL Execution time: "      << timeWallclock(t[0], t[6]) << "us\n";
  }
  delete[] softmax;
  delete[] FCResult;
}


/**
 * @brief Entry for running ResNet50 neural network.
 *
 * @note Neural network ResNet50 is divied into two seperate DPU
 *       Kernels：CONV and FC, because average pooling computation
 *       isn't supported by DPU@Zynq7020 platform. (This feature is
 *       already enabled on other DPU targets. Please contact us
 *       via dnndk@deephi.tech for more information. )
 *
 */
int main(void) {
  readPathsFromEnv();

  /* DPU Kernels/Tasks for running ResNet50 */
  DPUKernel *kernelConv;
  DPUKernel *kernelFC;
  DPUTask *taskConv;
  DPUTask *taskFC;

  /* Attach to DPU driver and prepare for running */
  dpuOpen();
  /* Create DPU Kernels for CONV & FC Nodes in ResNet50 */
  kernelConv = dpuLoadKernel(KERNEL_CONV);
  kernelFC = dpuLoadKernel(KERNEL_FC);
  /* Create DPU Tasks for CONV & FC Nodes in ResNet50 */
  taskConv = dpuCreateTask(kernelConv, 0);
  taskFC = dpuCreateTask(kernelFC, 0);

  /* Run CONV & FC Kernels for ResNet50 */
  runResnet50(taskConv, taskFC);

  /* Destroy DPU Tasks & free resources */
  dpuDestroyTask(taskConv);
  dpuDestroyTask(taskFC);
  /* Destroy DPU Kernels & free resources */
  dpuDestroyKernel(kernelConv);
  dpuDestroyKernel(kernelFC);
  /* Detach from DPU driver & free resources */
  dpuClose();

  return 0;
}
