/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLFullyConnectedLayer.h>

#include "autotune/tuner_fully_connected.h"

#include "ck_nntest_armcl.h"

using namespace CK;
using namespace CK::armcl;
using namespace arm_compute;

int main() {
  init_test();

  auto tuner = get_lws_tuner<CLTuner_FullyConnected>();
  init_armcl(tuner.get());

  auto data_layout = get_data_layout_from_env();
  Shape in_shape = get_input_shape_from_env();

  bool transpose_weights = getenv_i("CK_TRANSPOSE_WEIGHTS", 0);
  bool are_weights_reshaped = getenv_i("CK_WEIGHTS_RESHAPED", 0);

  CK::Shape out_shape;
  out_shape.num = in_shape.num;
  out_shape.height = getenv_i("CK_OUT_SHAPE_H", 1);
  out_shape.width = getenv_i("CK_OUT_SHAPE_W", 1);
  out_shape.channels = getenv_i("CK_OUT_SHAPE_C", 1);

  const size_t batch_count = in_shape.num;
  const size_t in_batch_size = in_shape.channels * in_shape.height * in_shape.width;
  const size_t out_batch_size = out_shape.channels * out_shape.height * out_shape.width;

  CLFullyConnectedLayer layer;

  CLTensor input, output;
  CLTensor weights;
  CLTensor biases;

  measure_setup([&]() {
    TensorShape native_in_shape(in_batch_size, batch_count);
    input.allocator()->init(TensorInfo(native_in_shape, 1, DataType::F32));

    TensorShape native_in_weights = transpose_weights ?
                                    TensorShape(in_batch_size, out_batch_size) :
                                    TensorShape(out_batch_size, in_batch_size);
    weights.allocator()->init(TensorInfo(native_in_weights, 1, DataType::F32));

    TensorShape native_in_biases(out_batch_size);
    biases.allocator()->init(TensorInfo(native_in_biases, 1, DataType::F32));

    TensorShape native_out(out_batch_size, batch_count);
    output.allocator()->init(TensorInfo(native_out, 1, DataType::F32));

#if defined(ARMCL_18_08_PLUS)
    FullyConnectedLayerInfo fc_info;
    fc_info.transpose_weights = transpose_weights;
    fc_info.are_weights_reshaped = are_weights_reshaped;
    fc_info.weights_trained_layout = data_layout == LAYOUT_NCHW ? DataLayout::NCHW : DataLayout::NHWC;
    layer.configure(&input, &weights, &biases, &output, fc_info);
#else
    layer.configure(&input, &weights, &biases, &output, transpose_weights, are_weights_reshaped);
#endif
    print_tensor_shape("Configured CL shape", &output);

    input.allocator()->allocate();
    weights.allocator()->allocate();
    biases.allocator()->allocate();
    output.allocator()->allocate();

    float *in_data = get_random_raw_data<float>(in_shape);
    print_input_raw_data(in_data, in_shape);
    copy_raw_data_to_tensor(&input, in_data, in_shape.data_count());
    print_tensor_data("ArmCL native input", &input);
    delete[] in_data;

    float weights_value = getenv_f("CK_IN_WEIGHTS_CONST_VALUE", 1);
    float *weights_data = get_const_raw_data(native_in_weights.total_size(), weights_value);
    copy_raw_data_to_tensor(&weights, weights_data, native_in_weights.total_size());
    delete[] weights_data;

    float biases_value = getenv_f("CK_IN_BIAS_CONST_VALUE", 0);
    float *biases_data = get_const_raw_data(native_in_biases.total_size(), biases_value);
    copy_raw_data_to_tensor(&biases, biases_data, native_in_biases.total_size());
    delete[] biases_data;
  });

  measure_test([&]() {
    layer.run();
    // Ensure all OpenCL jobs have finished.
    CLScheduler::get().sync();
  });

  print_tensor_data("ArmCL native output", &output);
  float *out_data = new float[out_shape.data_count()];
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
