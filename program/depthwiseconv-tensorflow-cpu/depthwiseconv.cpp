/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include "ck_nntest_tensorflow.h"

using namespace CK;
using namespace CK::TF;
using namespace tensorflow;
using namespace tensorflow::ops;

#define DEFAULT_IN_N 1
#define DEFAULT_IN_C 1
#define DEFAULT_IN_H 7
#define DEFAULT_IN_W 7
#define DEFAULT_DEPTHWISE_STRIDE 1
#define DEFAULT_DEPTHWISE_PAD 0
#define DEFAULT_DEPTHWISE_KERNEL 3
#define DEFAULT_DEPTHWISE_DEPTH_MULTIPLIER 1

int main() {
  init_test();

  Scope root = Scope::NewRootScope();

  // Prepare input data
  CK::Shape in_shape = get_input_shape_from_env(DEFAULT_IN_N, DEFAULT_IN_C, DEFAULT_IN_H, DEFAULT_IN_W);
  Tensor input(DT_FLOAT, TensorShape({in_shape.num, in_shape.height, in_shape.width, in_shape.channels}));
  float *in_data = get_random_raw_data<float>(in_shape);
  print_input_raw_data(in_data, in_shape);
  memcpy(input.flat<float>().data(), in_data, in_shape.data_count() * sizeof(float));
  delete[] in_data;

  // Prepare operation params
  int kernel_height = getenv_i("CK_DEPTHWISE_KERNEL", DEFAULT_DEPTHWISE_KERNEL);
  int kernel_width = getenv_i("CK_DEPTHWISE_KERNEL", DEFAULT_DEPTHWISE_KERNEL);
  int stride = getenv_i("CK_DEPTHWISE_STRIDE", DEFAULT_DEPTHWISE_STRIDE);
  int pad = getenv_i("CK_DEPTHWISE_PAD", DEFAULT_DEPTHWISE_PAD);
  int depth_multiplier = getenv_i("CK_DEPTHWISE_DEPTH_MULTIPLIER", DEFAULT_DEPTHWISE_DEPTH_MULTIPLIER);

  // Prepare output shape
  CK::Shape out_shape = CK::Shape::make_nchw(
                          in_shape.num,
                          in_shape.channels * depth_multiplier,
                          (in_shape.height - kernel_height + stride + 2 * pad) / stride,
                          (in_shape.width - kernel_width + stride + 2 * pad) / stride);

  printf("Calculated output image size: W=%d, H=%d\n", out_shape.width, out_shape.height);
  assert(out_shape.width > 0 && out_shape.height > 0);

  Tensor output(DT_FLOAT, TensorShape({out_shape.num, out_shape.height, out_shape.width, out_shape.channels}));

  // Prepare weights data
  // https://www.tensorflow.org/api_docs/python/tf/nn/depthwise_conv2d_native
  // filter / kernel tensor of shape [filter_height, filter_width, in_channels, channel_multiplier]
  Tensor weightTensor(DT_FLOAT, TensorShape({kernel_height, kernel_width, in_shape.channels, depth_multiplier}));
  CK::Shape weights_shape = CK::Shape::make_nchw(in_shape.channels, depth_multiplier, kernel_height, kernel_width);
  float *weights_data = get_random_raw_data<float>(weights_shape);
  memcpy(weightTensor.flat<float>().data(), weights_data, weights_shape.data_count() * sizeof(float));
  delete[] weights_data;

  // Prepare operation
  std::vector<Tensor> outputs;
  const char *test_node_name = "test_dwc";
  std::vector<int> strides = {1, stride, stride, 1};
  tensorflow::ops::DepthwiseConv2dNative depthwiseConv2dNative(
    root.WithOpName(test_node_name), input, weightTensor, strides,
    pad == 0 ? "VALID" : "SAME");

  // Prepare measurement
  RunOptions run_options;
  run_options.set_trace_level(RunOptions::FULL_TRACE);
  RunMetadata run_metadata;

  // Run test
  measure_test([&]() {
    ClientSession session(root);
    auto result = session.Run(run_options, {}, {depthwiseConv2dNative}, {}, &outputs, &run_metadata);
    TF_CHECK_OK(result);
  });

  // Get output data
  float *out_data = new float[out_shape.data_count()];
  memcpy(out_data, outputs[0].flat<float>().data(), out_shape.data_count() * sizeof(float));
  print_output_raw_data(out_data, out_shape);
  dump_output_raw_data(out_data, out_shape);
  delete[] out_data;

  process_metadata(run_metadata, test_node_name);

  finish_test();
  return 0;
}
