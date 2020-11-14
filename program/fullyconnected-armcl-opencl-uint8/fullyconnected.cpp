/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLFullyConnectedLayer.h>

#include "ck_nntest_armcl.h"

using namespace CK;
using namespace CK::armcl;
using namespace arm_compute;

int main() {
  init_test();
  init_armcl();

  Shape in_shape = get_input_shape_from_env();

  bool transpose_weights = getenv_i("CK_TRANSPOSE_WEIGHTS", 0);
  bool are_weights_reshaped = getenv_i("CK_WEIGHTS_RESHAPED", 0);

  CK::Shape out_shape;
  out_shape.num =  in_shape.num;
  out_shape.height = getenv_i("CK_OUT_SHAPE_H", 1);
  out_shape.width =  getenv_i("CK_OUT_SHAPE_W", 1);
  out_shape.channels = getenv_i("CK_OUT_SHAPE_C", 1);

  const size_t batch_count = in_shape.num;
  const size_t in_batch_size = in_shape.channels * in_shape.height * in_shape.width;
  const size_t out_batch_size = out_shape.channels * out_shape.height * out_shape.width;

  CLFullyConnectedLayer layer;

  CLTensor input, output;
  CLTensor weights;
  CLTensor biases;

  measure_setup([&]() {
    // Init input tensor
    TensorShape native_in_shape(in_batch_size, batch_count);
    TensorInfo in_tensor_info(native_in_shape, 1, DataType::QASYMM8);
    float in_data_min = 0;
    float in_data_max = 1;
    init_quantization_info(in_tensor_info, in_data_min, in_data_max);
    print_quantization_info_info("input", in_tensor_info);
    input.allocator()->init(in_tensor_info);

    // Init weights tensor
    TensorShape native_weights_shape = transpose_weights ?
                                       TensorShape(in_batch_size, out_batch_size) :
                                       TensorShape(out_batch_size, in_batch_size);
    TensorInfo weights_tensor_info(native_weights_shape, 1, DataType::QASYMM8);
    float weight_min = 0;
    float weight_max = 1;
    init_quantization_info(weights_tensor_info, weight_min, weight_max);
    print_quantization_info_info("weights", weights_tensor_info);
    weights.allocator()->init(weights_tensor_info);

    auto input_product_scale = in_tensor_info.quantization_info().scale * weights_tensor_info.quantization_info().scale;

    // Init biases tensor
    TensorShape native_biases_shape(out_batch_size);
    TensorInfo biases_tensor_info(native_biases_shape, 1, DataType::S32);
    float bias_min = 0;
    float bias_max = 1.0 / 255.0;
    init_quantization_info(biases_tensor_info, bias_min, bias_max);
    print_quantization_info_info("biases", biases_tensor_info);
    biases.allocator()->init(biases_tensor_info);

    // Init output tensor
    TensorShape native_out_shape(out_batch_size, batch_count);
    TensorInfo out_tensor_info(native_out_shape, 1, DataType::QASYMM8);
    out_tensor_info.set_quantization_info(QuantizationInfo(input_product_scale * 1.001, 0));
    print_quantization_info_info("output", out_tensor_info);
    output.allocator()->init(out_tensor_info);

    // Configure layer
    try {
      layer.configure(&input, &weights, &biases, &output, transpose_weights, are_weights_reshaped);
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

    // Fill input data
    uint8_t *in_data = get_random_raw_data<uint8_t>(in_shape, 0, 50);
    print_input_raw_data(in_data, in_shape);
    copy_raw_data_to_tensor(&input, in_data, in_shape.data_count());
    print_tensor_data("ArmCL native input", &input);
    delete[] in_data;

    // Fill weights data
    uint8_t weights_value = getenv_i("CK_IN_WEIGHTS_CONST_VALUE", 1);
    uint8_t *weights_data = get_const_raw_data<uint8_t>(native_weights_shape.total_size(), weights_value);
    copy_raw_data_to_tensor(&weights, weights_data, native_weights_shape.total_size());
    delete[] weights_data;

    // Fill biases data
    int32_t biases_value = getenv_i("CK_IN_BIAS_CONST_VALUE", 0);
    int32_t *biases_data = get_const_raw_data<int32_t>(native_biases_shape.total_size(), biases_value);
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
    // Make sure all the OpenCL jobs are done executing
    CLScheduler::get().sync();
  });

  // Get and process output data
  print_tensor_data("ArmCL native output", &output);
  uint8_t *out_data = new uint8_t[out_shape.data_count()];
  copy_raw_data_from_tensor(&output, out_data, out_shape.data_count());
  print_output_raw_data(out_data, out_shape);
  dump_output_raw_data(out_data, out_shape);
  delete[] out_data;

  input.allocator()->free();
  weights.allocator()->free();
  biases.allocator()->free();
  output.allocator()->free();

  finish_test();
  return 0;
}
