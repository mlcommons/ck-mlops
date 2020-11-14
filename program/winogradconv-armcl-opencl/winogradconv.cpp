/*
 * Copyright (c) 2018 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLWinogradConvolutionLayer.h>

#include "ck_nntest_armcl.h"

using namespace CK;
using namespace CK::armcl;
using namespace arm_compute;

#define DEFAULT_IN_N 1
#define DEFAULT_IN_C 1
#define DEFAULT_IN_H 5
#define DEFAULT_IN_W 5
#define DEFAULT_KERNEL 5
#define DEFAULT_STRIDE 1
#define DEFAULT_PAD 0
#define DEFAULT_OUT_C 1

int main() {
  init_test();

  arm_compute::ICLTuner *tuner = nullptr;
  // TODO: Provide a custom winogradconv tuner.
  init_armcl(tuner);

  CLTensor input, output, weights, biases;
  CLWinogradConvolutionLayer layer;

  auto data_layout = get_data_layout_from_env();

  // Prepare input shape
  Shape in_shape = get_input_shape_from_env(DEFAULT_IN_N, DEFAULT_IN_C,
                                            DEFAULT_IN_H, DEFAULT_IN_W);
  TensorShape native_in_shape = to_tensor_shape(in_shape, data_layout);

  // Prepare operation params
  bool enable_fast_math = static_cast<bool>(getenv_i("CK_ENABLE_FAST_MATH", 1));
  size_t in_feature_maps = static_cast<size_t>(in_shape.channels);
  size_t out_feature_maps = static_cast<size_t>(getenv_i("CK_OUT_SHAPE_C", DEFAULT_OUT_C));
  printf("in_feature_maps=%d, out_feature_maps=%d\n",
         static_cast<int>(in_feature_maps), static_cast<int>(out_feature_maps));

  ConvolutionParams conv_params = get_conv_params_from_env(
                                    DEFAULT_KERNEL, DEFAULT_STRIDE, DEFAULT_PAD);
  PadStrideInfo pad_stride_info(conv_params.stride, conv_params.stride,
                                conv_params.pad, conv_params.pad);

  // Prepare weights shape
  TensorShape native_weights_shape = data_layout == LAYOUT_NCHW ?
    TensorShape(conv_params.kernel, conv_params.kernel, in_feature_maps, out_feature_maps) :
    TensorShape(in_feature_maps, conv_params.kernel, conv_params.kernel, out_feature_maps);

  // Prepare biases shape
  TensorShape native_biases_shape(out_feature_maps);

  // Prepare output shape
  Shape out_shape;
  out_shape.channels = out_feature_maps;
  out_shape.num = in_shape.num;
  out_shape.width = (in_shape.width + 2 * conv_params.pad - conv_params.kernel) / conv_params.stride + 1;
  out_shape.height = (in_shape.height + 2 * conv_params.pad - conv_params.kernel) / conv_params.stride + 1;
  printf("Calculated output image size: W=%d, H=%d\n", out_shape.width, out_shape.height);
  assert(out_shape.width > 0 && out_shape.height > 0);
  TensorShape native_out_shape = to_tensor_shape(out_shape, data_layout);

  measure_setup([&]() {
    input.allocator()->init(make_tensor_info(native_in_shape, DataType::F32, data_layout));
    output.allocator()->init(make_tensor_info(native_out_shape, DataType::F32, data_layout));
    weights.allocator()->init(make_tensor_info(native_weights_shape, DataType::F32, data_layout));
    biases.allocator()->init(TensorInfo(native_biases_shape, Format::F32));

    layer.configure(&input, &weights, &biases, &output, pad_stride_info, ActivationLayerInfo(), enable_fast_math);

    // Prepare input data
    input.allocator()->allocate();
    float *in_data = get_random_raw_data<float>(in_shape);
    //float* in_data = get_const_raw_data<float>(in_shape.data_count(), 1.f);
    print_input_raw_data(in_data, in_shape);
    copy_raw_data_to_tensor(&input, in_data, in_shape);
    delete[] in_data;

    // Prepare output data buffer
    print_tensor_shape("Configured CL shape", &output);
    output.allocator()->allocate();

    // Prepare weights data
    // We use const weight and biases to match results with Caffe test
    // There is not way in Caffe to initialize weights and biases with random values using specified seed
    weights.allocator()->allocate();
    float weights_value = getenv_f("CK_IN_WEIGHTS_CONST_VALUE", 1.1);
    float *weights_data = get_const_raw_data(native_weights_shape.total_size(), weights_value);
    copy_raw_data_to_tensor(&weights, weights_data, native_weights_shape.total_size());
    delete[] weights_data;

    // Prepare biases data
    biases.allocator()->allocate();
    float biases_value = getenv_f("CK_IN_BIAS_CONST_VALUE", 1.1);
    float *biases_data = get_const_raw_data(native_biases_shape.total_size(), biases_value);
    copy_raw_data_to_tensor(&biases, biases_data, native_biases_shape.total_size());
    delete[] biases_data;
  });

  measure_test([&]() {
    layer.run();
    // Ensure that all OpenCL jobs have completed.
    CLScheduler::get().sync();
  });

  // Process output data
  float *out_data = new float[out_shape.data_count()];
  copy_raw_data_from_tensor(&output, out_data, out_shape);
  print_output_raw_data(out_data, out_shape);
  dump_output_raw_data(out_data, out_shape);
  delete[] out_data;

  input.allocator()->free();
  output.allocator()->free();
  weights.allocator()->free();
  biases.allocator()->free();

  finish_test();
  return 0;
}
