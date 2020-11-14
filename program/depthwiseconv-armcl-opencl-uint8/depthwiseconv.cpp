/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLDepthwiseConvolutionLayer.h>
#include <arm_compute/core/Types.h>

#include "ck_nntest_armcl.h"
#include <memory>

using namespace CK;
using namespace CK::armcl;
using namespace arm_compute;

static const int KERNEL_W = 3;
static const int KERNEL_H = 3;

enum TENSOR {
  INPUT, WEIGHTS, BIASES, OUTPUT,

  TENSOR_COUNT
};

void init_tensor_data(CLTensor *tensor, const Shape &shape, uint8_t range_min, uint8_t range_max) {
  uint8_t *in_data = get_random_raw_data<uint8_t>(shape, range_min, range_max);
  print_input_raw_data(in_data, shape);
  copy_raw_data_to_tensor(tensor, in_data, shape);
  delete[] in_data;
}

int main() {
  init_test();
  init_armcl();

  Shape input_shape = get_input_shape_from_env();
  Shape kernel_shape = Shape::make_chw(input_shape.channels, KERNEL_H, KERNEL_W);

  unsigned int stride = getenv_i("CK_DEPTHWISE_STRIDE", 1);
  unsigned int pad = getenv_i("CK_DEPTHWISE_PAD", 0);
  PadStrideInfo conv_info(stride, stride, pad, pad);

  Shape output_shape = Shape::make_nchw(
                         input_shape.num,
                         kernel_shape.channels,
                         (input_shape.width - kernel_shape.width + stride + 2 * pad) / stride,
                         (input_shape.height - kernel_shape.height + stride + 2 * pad) / stride);

  CLTensor tensors[TENSOR_COUNT];

  TensorShape tensor_shapes[TENSOR_COUNT] = {
    [INPUT]   = to_tensor_shape_whcn(input_shape),
    [WEIGHTS] = to_tensor_shape_whcn(kernel_shape),
    [BIASES]  = TensorShape(static_cast<size_t>(kernel_shape.channels)),
    [OUTPUT]  = to_tensor_shape_whcn(output_shape)
  };

  const uint8_t input_max = 30;

  const QuantizationInfo input_qi = get_quantization_info(0, input_max);
  const QuantizationInfo weights_qi = get_quantization_info(0, 1);

  const QuantizationInfo tensor_qi[TENSOR_COUNT] = {
    [INPUT]   = input_qi,
    [WEIGHTS] = weights_qi,
    [BIASES]  = get_quantization_info(0, 1.0 / 255.0),
    [OUTPUT]  = QuantizationInfo(input_qi.scale *weights_qi.scale * 1.001, 0)
  };

  CLDepthwiseConvolutionLayer3x3 layer;

  measure_setup([&]() {
    for (int i = 0; i < TENSOR_COUNT; ++i) {
      auto data_type = i == BIASES ? DataType::S32 : DataType::QASYMM8;
      TensorInfo tensor_info(tensor_shapes[i], 1, data_type);
      tensor_info.set_quantization_info(tensor_qi[i]);
      print_quantization_info_info("tensor", tensor_info);
      tensors[i].allocator()->init(tensor_info);
    }

    layer.configure(tensors + INPUT, tensors + OUTPUT, tensors + WEIGHTS, tensors + BIASES, conv_info);

    for (int i = 0; i < TENSOR_COUNT; ++i) {
      tensors[i].allocator()->allocate();
    }

    init_tensor_data(tensors + INPUT, input_shape, 0, input_max);

    // Init weights with constant value to match the other programs' behaviour
    //init_tensor_data(tensors + WEIGHTS, kernel_shape, 0, 10);
    uint8_t weights_value = getenv_i("CK_IN_WEIGHTS_CONST_VALUE", 1);
    uint8_t *weights_data = get_const_raw_data<uint8_t>(kernel_shape.data_count(), weights_value);
    copy_raw_data_to_tensor(tensors + WEIGHTS, weights_data, kernel_shape);
    delete[] weights_data;

    // The same for biases
    //init_tensor_data(tensors + BIASES, to_ck_shape(tensor_shapes[BIASES]), 0, 1);
    int32_t biases_value = getenv_f("CK_IN_BIAS_CONST_VALUE", 0);
    int32_t *biases_data = get_const_raw_data(tensor_shapes[BIASES].total_size(), biases_value);
    copy_raw_data_to_tensor(tensors + BIASES, biases_data, tensor_shapes[BIASES].total_size());
    delete[] biases_data;
  });

  measure_test([&]() {
    layer.run();

    // Make sure all the OpenCL jobs are done executing
    CLScheduler::get().sync();
  });

  uint8_t *out_data = new uint8_t[output_shape.data_count()];
  copy_raw_data_from_tensor(tensors + OUTPUT, out_data, output_shape);
  print_output_raw_data(out_data, output_shape);
  dump_output_raw_data(out_data, output_shape);
  delete[] out_data;

  for (int i = 0; i < TENSOR_COUNT; ++i) {
    tensors[i].allocator()->free();
  }

  finish_test();
  return 0;
}
