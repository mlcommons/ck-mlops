/*
 * Copyright (c) 2017-2018 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#if defined(ARMCL_18_05_PLUS)
#include <arm_compute/runtime/CL/functions/CLGEMMConvolutionLayer.h>
#else
#include <arm_compute/runtime/CL/functions/CLConvolutionLayer.h>
#endif

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
  init_armcl();

  CLTensor input, output, weights, biases;
#if defined(ARMCL_18_05_PLUS)
  CLGEMMConvolutionLayer layer;
#else
  CLConvolutionLayer layer;
#endif

  // Prepare input shape
  auto data_layout = get_data_layout_from_env();
  Shape in_shape = get_input_shape_from_env(DEFAULT_IN_N, DEFAULT_IN_C,
                                            DEFAULT_IN_H, DEFAULT_IN_W);
  TensorShape native_in_shape = to_tensor_shape(in_shape, data_layout);

  // Prepare operation params
  size_t in_feature_maps = static_cast<size_t>(in_shape.channels);
  size_t out_feature_maps = static_cast<size_t>(getenv_i("CK_OUT_SHAPE_C", DEFAULT_OUT_C));
  printf("in_feature_maps=%d, out_feature_maps=%d\n",
         static_cast<int>(in_feature_maps), static_cast<int>(out_feature_maps));

  ConvolutionParams conv_params = get_conv_params_from_env(
                                    DEFAULT_KERNEL, DEFAULT_STRIDE, DEFAULT_PAD);
  PadStrideInfo pad_stride_info(conv_params.stride, conv_params.stride,
                                conv_params.pad, conv_params.pad);

  // Prepare weights shape
  TensorShape native_weights_shape(conv_params.kernel, conv_params.kernel,
                                   in_feature_maps, out_feature_maps);

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
    // Prepare input tensor
    TensorInfo in_tensor_info = make_tensor_info(native_in_shape, DataType::QASYMM8, data_layout);
    float in_data_min = -40;
    float in_data_max = 1000;
    init_quantization_info(in_tensor_info, in_data_min, in_data_max);
    print_quantization_info_info("input", in_tensor_info);
    input.allocator()->init(in_tensor_info);

    // Prepare weights tensor
    TensorInfo weights_tensor_info(native_weights_shape, 1, DataType::QASYMM8);
    float weight_min = -10;
    float weight_max = 1100;
    init_quantization_info(weights_tensor_info, weight_min, weight_max);
    print_quantization_info_info("weights", weights_tensor_info);
    weights.allocator()->init(weights_tensor_info);

    auto input_product_scale = in_tensor_info.quantization_info().scale * weights_tensor_info.quantization_info().scale;

    // Prepare biases tensor
    TensorInfo biases_tensor_info(native_biases_shape, 1, DataType::S32);
    float bias_min = 0;
    float bias_max = 255 * input_product_scale;
    init_quantization_info(biases_tensor_info, bias_min, bias_max);
    print_quantization_info_info("biases", biases_tensor_info);
    biases.allocator()->init(biases_tensor_info);

    // Prepare output tensor
    TensorInfo out_tensor_info = make_tensor_info(native_out_shape, DataType::QASYMM8, data_layout);
    out_tensor_info.set_quantization_info(QuantizationInfo(input_product_scale * 2, 0));
    print_quantization_info_info("output", out_tensor_info);
    output.allocator()->init(out_tensor_info);

    // Configure layer
    try {
      layer.configure(&input, &weights, &biases, &output, pad_stride_info);
      print_tensor_shape("Configured CL shape", &output);
    }
    catch (const cl::Error &err) {
      printf("ArmCL exception while configure:\nwhat=%s\nerr_code=%d\n", err.what(), err.err());
      abort();
    }

    // Allocate tensors
    input.allocator()->allocate();
    weights.allocator()->allocate();
    biases.allocator()->allocate();
    output.allocator()->allocate();

    // Prepare input data
    uint8_t *in_data = get_random_raw_data<uint8_t>(in_shape, 0, 10);
    print_input_raw_data(in_data, in_shape);
    if (data_layout == LAYOUT_NHWC)
      convert_data_layout_NCHW_to_NHWC(in_data, in_shape);
    copy_raw_data_to_tensor(&input, in_data, in_shape);
    delete[] in_data;

    // Prepare weights data
    uint8_t weights_value = getenv_i("CK_IN_WEIGHTS_CONST_VALUE", 1);
    uint8_t *weights_data = get_const_raw_data(native_weights_shape.total_size(), weights_value);
    copy_raw_data_to_tensor(&weights, weights_data, native_weights_shape.total_size());
    delete[] weights_data;

    // Prepare biases data
    int32_t biases_value = getenv_f("CK_IN_BIAS_CONST_VALUE", 1);
    int32_t *biases_data = get_const_raw_data(native_biases_shape.total_size(), biases_value);
    copy_raw_data_to_tensor(&biases, biases_data, native_biases_shape.total_size());
    delete[] biases_data;
  });

  measure_test([&]() {
    try {
      layer.run();
    }
    catch (const cl::Error &err) {
      printf("ArmCL exception while run:\nwhat=%s\nerr_code=%d\n", err.what(), err.err());
      abort();
    }
    // Ensure that all OpenCL jobs have completed.
    CLScheduler::get().sync();
  });

  // Process output data
  uint8_t *out_data = new uint8_t[out_shape.data_count()];
  copy_raw_data_from_tensor(&output, out_data, out_shape);
  // We should change data layout to match the results with TensorFlow tests
  if (data_layout == LAYOUT_NHWC)
    convert_data_layout_NHWC_to_NCHW(out_data, out_shape);
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
