/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include "ck_nntest_tensorflow.h"

using namespace std;
using namespace CK;
using namespace CK::TF;
using namespace tensorflow;
using namespace tensorflow::ops;

#define DEFAULT_IN_N 1
#define DEFAULT_IN_C 1
#define DEFAULT_IN_H 7
#define DEFAULT_IN_W 7
#define DEFAULT_KERNEL 7
#define DEFAULT_STRIDE 1
#define DEFAULT_PAD 0
#define DEFAULT_OUT_C 1

int main() {
  init_test();

  Scope root = Scope::NewRootScope();

  // Prepare input data
  CK::Shape in_shape = get_input_shape_from_env(DEFAULT_IN_N, DEFAULT_IN_C, DEFAULT_IN_H, DEFAULT_IN_W);
  Tensor input(DT_FLOAT, TensorShape({in_shape.num, in_shape.height, in_shape.width, in_shape.channels}));
  float *in_data = get_random_raw_data<float>(in_shape);
  print_input_raw_data(in_data, in_shape);
  convert_data_layout_NCHW_to_NHWC(in_data, in_shape);
  memcpy(input.flat<float>().data(), in_data, in_shape.data_count() * sizeof(float));
  delete[] in_data;

  // Prepare operation params
  int in_feature_maps = in_shape.channels;
  int out_feature_maps = getenv_i("CK_OUT_SHAPE_C", DEFAULT_OUT_C);
  cout << "in_feature_maps=" << in_feature_maps << ", out_feature_maps=" << out_feature_maps << endl;

  ConvolutionParams conv_params = get_conv_params_from_env(DEFAULT_KERNEL, DEFAULT_STRIDE, DEFAULT_PAD);

  // Prepare output shape
  CK::Shape out_shape;
  out_shape.num = in_shape.num;
  out_shape.channels = out_feature_maps;
  out_shape.height = (in_shape.height + 2 * conv_params.pad - conv_params.kernel) / conv_params.stride + 1;
  out_shape.width = (in_shape.width + 2 * conv_params.pad - conv_params.kernel) / conv_params.stride + 1;
  printf("ConvolutionParams: conv_params.pad=%d, conv_params.kernel=%d\n", conv_params.pad, conv_params.kernel);
  printf("Calculated output image size: W=%d, H=%d\n", out_shape.width, out_shape.height);
  assert(out_shape.width > 0 && out_shape.height > 0);

  Tensor output(DT_FLOAT, TensorShape({out_shape.num, out_shape.height, out_shape.width, out_shape.channels}));

  // Prepare weights data
  Tensor weightTensor(DT_FLOAT, TensorShape({
    static_cast<int>(conv_params.kernel),
    static_cast<int>(conv_params.kernel),
    in_feature_maps,
    out_feature_maps
  }));
  // We use const weight and biases to match results with Caffe test
  // There is not way in Caffe to initialize weights and biases with random values using specified seed
  int weight_count = conv_params.kernel * conv_params.kernel * in_shape.channels * out_shape.channels;
  float weights_value = getenv_f("CK_IN_WEIGHTS_CONST_VALUE", 1.1);
  float *weights_data = get_const_raw_data(weight_count, weights_value);
  memcpy(weightTensor.flat<float>().data(), weights_data, weight_count * sizeof(float));
  delete[] weights_data;

  // Prepare biases data
  int bias_count = out_shape.channels;
  float biases_value = getenv_f("CK_IN_BIAS_CONST_VALUE", 1.1);
  float *biases_data = get_const_raw_data(bias_count, biases_value);
  Tensor biasTensor(DT_FLOAT, TensorShape({bias_count}));
  memcpy(biasTensor.flat<float>().data(), biases_data, bias_count * sizeof(float));
  delete[] biases_data;

  // Prepare operation
  std::vector<Tensor> outputs;
  const char *test_node_name = "test_conv";
  std::vector<int> strides = {1, static_cast<int>(conv_params.stride), static_cast<int>(conv_params.stride), 1};
  tensorflow::ops::Conv2D conv2D(root.WithOpName(test_node_name), input, weightTensor, strides, 
    conv_params.pad == 0 ? "VALID" : "SAME");

  tensorflow::ops::BiasAdd biasAdd(root.WithOpName("biasAdd"), conv2D, biasTensor);

  // Prepare measurement
  RunOptions run_options;
  run_options.set_trace_level(RunOptions::FULL_TRACE);
  RunMetadata run_metadata;
  
  // Run test
  measure_test([&]() {
    ClientSession session(root);
    auto result = session.Run(run_options, {}, {biasAdd}, {}, &outputs, &run_metadata);
    TF_CHECK_OK(result);
  });

  // Get output data
  float *out_data = new float[out_shape.data_count()];
  memcpy(out_data, outputs[0].flat<float>().data(), out_shape.data_count() * sizeof(float));
  convert_data_layout_NHWC_to_NCHW(out_data, out_shape);
  print_output_raw_data(out_data, out_shape);
  dump_output_raw_data(out_data, out_shape);
  delete[] out_data;

  process_metadata(run_metadata, test_node_name);

  finish_test();
  return 0;
}
