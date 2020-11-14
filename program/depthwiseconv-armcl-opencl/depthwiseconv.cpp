/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLDepthwiseConvolutionLayer.h>
#include <arm_compute/core/Types.h>

#include "autotune/tuner_depthwise_convolution.h"

#include "ck_nntest_armcl.h"
#include <memory>

using namespace CK;
using namespace CK::armcl;
using namespace arm_compute;

static const int KERNEL_W = 3;
static const int KERNEL_H = 3;

enum TENSOR {
  INPUT, WEIGHTS, OUTPUT,

  TENSOR_COUNT
};

void init_tensor_data(CLTensor *tensor, const Shape &shape, const char *env_var, const char *title) {
  float *in_data = get_random_raw_data<float>(shape);
  // We should change data layout to match the results with TensorFlow tests
  convert_data_layout_NHWC_to_NCHW(in_data, shape);
  log_raw_data(in_data, shape, env_var, title);
  copy_raw_data_to_tensor(tensor, in_data, shape);
  delete[] in_data;
}


class LayerWrapper {
public:
  LayerWrapper() : layer(NULL), layer3x3(NULL) {
    int use_3x3_layer = getenv_i("CK_DEPTHWISE_3X3", 0);
    if (use_3x3_layer) {
      layer3x3 = new CLDepthwiseConvolutionLayer3x3;
      printf("Using layer CLDepthwiseConvolutionLayer3x3\n");
    }
    else {
      layer = new CLDepthwiseConvolutionLayer;
      printf("Using layer CLDepthwiseConvolutionLayer\n");
    }
  }

  ~LayerWrapper() {
    delete layer;
    delete layer3x3;
  }

  void configure(ICLTensor *input, const ICLTensor *weights, const ICLTensor *biases, ICLTensor *output,
                 const PadStrideInfo &conv_info) {
    if (layer3x3) {
      layer3x3->configure(input, weights, biases, output, conv_info);
    }
    else {
      layer->configure(input, weights, biases, output, conv_info);
    }
  }

  void run() {
    if (layer3x3) {
      layer3x3->run();
    }
    else {
      layer->run();
    }
  }

private:
  CLDepthwiseConvolutionLayer *layer;
  CLDepthwiseConvolutionLayer3x3 *layer3x3;
};

int main() {
  init_test();

  auto tuner = get_lws_tuner<CLTuner_DepthwiseConvolution>();
  init_armcl(tuner.get());

  auto data_layout = get_data_layout_from_env();
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

  LayerWrapper layer;

  measure_setup([&]() {
    TensorShape tensor_shapes[TENSOR_COUNT] = {
      [INPUT]   = to_tensor_shape(input_shape, data_layout),
      [WEIGHTS] = to_tensor_shape(kernel_shape, data_layout),
      [OUTPUT]  = to_tensor_shape(output_shape, data_layout)
    };

    for (int i = 0; i < TENSOR_COUNT; ++i) {
      tensors[i].allocator()->init(make_tensor_info(tensor_shapes[i], DataType::F32, data_layout));
    }

    layer.configure(tensors + INPUT, tensors + WEIGHTS, NULL, tensors + OUTPUT, conv_info);

    for (int i = 0; i < TENSOR_COUNT; ++i) {
      tensors[i].allocator()->allocate();
    }

    init_tensor_data(tensors + INPUT, input_shape, "CK_PRINT_IN_TENSOR", "INPUT");
    init_tensor_data(tensors + WEIGHTS, kernel_shape, "CK_PRINT_WEIGHTS_TENSOR", "WEIGHTS");
  });

  measure_test([&]() {
    layer.run();
    // Ensure all OpenCL jobs have finished.
    CLScheduler::get().sync();
  });

  float *out_data = new float[output_shape.data_count()];
  copy_raw_data_from_tensor(tensors + OUTPUT, out_data, output_shape);
  // We should change data layout to match the results with TensorFlow tests
  convert_data_layout_NCHW_to_NHWC(out_data, output_shape);
  print_output_raw_data(out_data, output_shape);
  dump_output_raw_data(out_data, output_shape);
  delete[] out_data;

  for (int i = 0; i < TENSOR_COUNT; ++i) {
    tensors[i].allocator()->free();
  }

  finish_test();
  fflush(stdout);
  return 0;
}
