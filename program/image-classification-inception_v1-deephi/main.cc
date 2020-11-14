/*
 * Copyright (c) 2016-2018 DeePhi Tech, Inc.
 *
 * All Rights Reserved. No part of this publication may be reproduced
 * or transmitted in any form or by any means without the prior written
 * permission of DeePhi Tech, Inc.
 *
 * Filename: main.cc
 * Version: 2.05
 *
 * Description :
 * Sample source code to illustrate how to deploy GoogLeNet neural network
 * on DeePhi DPU platform.
 */
#include <assert.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <fstream>
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

/* 3.16GOP times calculation for GoogLeNet CONV */
#define GOOGLENET_WORKLOAD_CONV (3.16f)
/* (2.048/1000)GOP times calculation for GoogLeNet FC */
#define GOOGLENET_WORKLOAD_FC (2.048f / 1000)

#define KERNEL_CONV "inception_v1_0"
#define KERNEL_FC "inception_v1_2"

#define TASK_CONV_INPUT "conv1_7x7_s2"
#define TASK_CONV_OUTPUT "inception_5b_output"
#define TASK_FC_INPUT "loss3_classifier"
#define TASK_FC_OUTPUT "loss3_classifier"

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
void ListImages(std::string const &path, std::vector<std::string> &images) {
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
      std::string name = entry->d_name;
      std::string ext = name.substr(name.find_last_of(".") + 1);
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
void LoadWords(std::string const &path, std::vector<std::string> &kinds) {
  kinds.clear();
  std::fstream fkinds(path);
  if (fkinds.fail()) {
    fprintf(stderr, "Error : Open %s failed.\n", path.c_str());
    exit(1);
  }
  std::string kind;
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
void TopK(const float *d, int size, int k, std::vector<std::string> &vkind) {
  assert(d && size > 0 && k > 0);
  std::priority_queue<std::pair<float, int>> q;

  for (auto i = 0; i < size; ++i) {
    q.push(std::pair<float, int>(d[i], i));
  }

  for (auto i = 0; i < k; ++i) {
    std::pair<float, int> ki = q.top();
    fprintf(stdout, "top[%d] prob = %-8f  name = %s\n", i, d[ki.second],
            vkind[ki.second].c_str());
    q.pop();
  }
}

/**
 * @brief Compute average pooling on CPU
 *
 * @param conv - pointer to GoogLeNet CONV Task
 * @param fc - pointer to GoogLeNet CONV Task
 *
 * @return none
 */
void CPUCalcAvgPool(DPUTask *conv, DPUTask *fc) {
  assert(conv && fc);

  DPUTensor *conv_out_tensor = dpuGetOutputTensor(conv, TASK_CONV_OUTPUT);

  /* Get size of the output Tensor */
  int tensorSize = dpuGetTensorSize(conv_out_tensor);
  /* Get height dimension of the output Tensor */
  int outHeight = dpuGetTensorHeight(conv_out_tensor);
  /* Get width dimension of the output Tensor */
  int outWidth = dpuGetTensorWidth(conv_out_tensor);

  /**
   * Get the channels of the last inception to compute the output Node's
   * actual output channel.
   */
  int outChannel = dpuGetTensorChannel(conv_out_tensor);

  /* Allocate the memory and store conv's output after conversion */
  float *outBuffer = new float[tensorSize];
  dpuGetOutputTensorInHWCFP32(conv, TASK_CONV_OUTPUT, outBuffer, tensorSize);

  /* Get the input address to the first Node of FC Task */
  int8_t *fcInput = dpuGetInputTensorAddress(fc, TASK_FC_INPUT);
  /* Get scale value for the first input Node of FC task */
  float scaleFC = dpuGetInputTensorScale(fc, TASK_FC_INPUT);
  int length = outHeight * outWidth;
  float avg = static_cast<float>(length);
  for (int i = 0; i < outChannel; i++) {
    float sum = 0.0f;
    for (int j = 0; j < length; j++) {
      sum += outBuffer[outChannel * j + i];
    }
    /* Compute average and set into the first input Node of FC Task */
    fcInput[i] = static_cast<int8_t>(sum / avg * scaleFC);
  }

  delete[] outBuffer;
}

/**
 * @brief Run DPU CONV Task and FC Task for GoogLeNet
 *
 * @param taskConv - pointer to GoogLeNet CONV Task
 * @param taskFC - pointer to GoogLeNet FC Task
 *
 * @return none
 */
void runGoogLeNet(DPUTask *taskConv, DPUTask *taskFC) {
  assert(taskConv && taskFC);
  
  /* Mean value for GoogLeNet specified in Caffe prototxt */
  vector<string> kinds, images;

  /* Load all image names */
  ListImages(baseImagePath, images);
  if (images.size() == 0) {
    cerr << "\nError: No images found in " << baseImagePath << endl;
    return;
  }

  /* Load all class descriptions.*/
  LoadWords(kindsPath, kinds);
  /* Get channel count of the output Tensor for FC Task  */
  int channel = dpuGetOutputTensorChannel(taskFC, TASK_FC_OUTPUT);
  float *softmax = new float[channel];
  float *result = new float[channel];
  for (auto &image_name : images) {
    /* Wallclock timestamps */
    const size_t n = 7;
    struct timeval t[n];

    gettimeofday(&t[0], NULL);

    cout << "\nLoad image : " << image_name << endl;
    /* Load image and Set image into DPU Task for GoogLeNet */
    Mat image = imread(baseImagePath + image_name);
    dpuSetInputImage2(taskConv, TASK_CONV_INPUT, image);

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
    dpuGetOutputTensorInHWCFP32(taskFC, TASK_FC_OUTPUT, result, channel);

    gettimeofday(&t[5], NULL);

    /* Run SOFTMAX on CPU */
    CPUCalcSoftmax(result, channel, softmax);
    
    gettimeofday(&t[6], NULL);

    /* Show TOP5 classification results */
    TopK(softmax, channel, 5, kinds);

    /* Output DPU and WALLCLOCK profiling times in microseconds */
    cout << "Profiling info:\n";
    long long timeProf;
    /* Output DPU execution time of CONV Task */
	timeProf = dpuGetTaskProfile(taskConv);
    cout << "  DPU CONV Execution time: " << (timeProf * 1.0f) << "us\n";
    float convProf = (GOOGLENET_WORKLOAD_CONV / timeProf) * 1000000.0f;
    cout << "  DPU CONV Performance: " << convProf << "GOPS\n";
    /* Output DPU execution time of FC Task */
    timeProf = dpuGetTaskProfile(taskFC);
    cout << "  DPU FC Execution time: " << (timeProf * 1.0f) << "us\n";
    float fcProf = (GOOGLENET_WORKLOAD_FC / timeProf) * 1000000.0f;
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
  delete[] result;
}

/**
 * @brief Entry for running GoogLeNet neural network.
 *
 * @note DNNDK APIs prefixed with "dpu" are used to easily program &
 *       deploy GoogLeNet on DPU platform.
 *
 */
int main(int argc, char *argv[]) {
  readPathsFromEnv();

  /* DPU Kernels/Tasks for running GoogLeNet */
  DPUKernel *kernelConv;
  DPUKernel *kernelFC;
  DPUTask *taskConv;
  DPUTask *taskFC;

  /* Attach to DPU driver and prepare for running */
  dpuOpen();

  /* Create DPU Kernels for CONV & FC Nodes in GoogLeNet */
  kernelConv = dpuLoadKernel(KERNEL_CONV);
  kernelFC = dpuLoadKernel(KERNEL_FC);

  /* Create DPU Tasks for CONV & FC Nodes in GoogLeNet */
  taskConv = dpuCreateTask(kernelConv, 0);
  taskFC = dpuCreateTask(kernelFC, 0);

  /* Run CONV & FC Kernels for GoogLeNet */
  runGoogLeNet(taskConv, taskFC);

  /* Destroy DPU Tasks & free resources */
  dpuDestroyTask(taskConv);
  dpuDestroyTask(taskFC);

  /* Destroy DPU Kernels & free resources */
  dpuDestroyKernel(kernelConv);
  dpuDestroyKernel(kernelFC);

  /* Detach from DPU driver & release resources */
  dpuClose();

  return 0;
}
