/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * See CK LICENSE for licensing details.
 * See CK COPYRIGHT for copyright details.
 */

#ifndef CK_NNTEST_CAFFE_CONV_H
#define CK_NNTEST_CAFFE_CONV_H

#include <caffe/blob.hpp>
#include <caffe/layers/conv_layer.hpp>

#include "ck_nntest_common.h"

#define DEFAULT_IN_N 1
#define DEFAULT_IN_C 1
#define DEFAULT_IN_H 7
#define DEFAULT_IN_W 7
#define DEFAULT_KERNEL 7
#define DEFAULT_STRIDE 1
#define DEFAULT_PAD 0
#define DEFAULT_OUT_C 1

typedef caffe::Blob<float> FloatBlob;

namespace CK {
namespace Caffe {

inline void test_convolution(bool use_im2col) {
  init_test();

  Shape in_shape = get_input_shape_from_env(DEFAULT_IN_N, DEFAULT_IN_C,
                                            DEFAULT_IN_H, DEFAULT_IN_W);

  FloatBlob *input = new FloatBlob(
    in_shape.num, in_shape.channels, in_shape.height, in_shape.width);
  std::vector<FloatBlob *> inputs;
  inputs.push_back(input);

  FloatBlob *output = new FloatBlob();
  std::vector<FloatBlob *> outputs;
  outputs.push_back(output);

  // Prepare operation params
  int out_feature_maps = getenv_i("CK_OUT_SHAPE_C", DEFAULT_OUT_C);
  printf("out_feature_maps=%d\n", out_feature_maps);

  ConvolutionParams conv_params = get_conv_params_from_env(
                                    DEFAULT_KERNEL, DEFAULT_STRIDE, DEFAULT_PAD);

  caffe::LayerParameter layer_param;
  caffe::ConvolutionParameter *conv_param = layer_param.mutable_convolution_param();
  conv_param->set_num_output(out_feature_maps);
  conv_param->set_kernel_h(conv_params.kernel);
  conv_param->set_kernel_w(conv_params.kernel);
  conv_param->set_stride_h(conv_params.stride);
  conv_param->set_stride_w(conv_params.stride);
  conv_param->set_pad_h(conv_params.pad);
  conv_param->set_pad_w(conv_params.pad);
  conv_param->set_force_nd_im2col(use_im2col);
  conv_param->mutable_weight_filler()->set_type("constant");
  conv_param->mutable_weight_filler()->set_value(getenv_f("CK_IN_WEIGHTS_CONST_VALUE", 1.1));
  conv_param->mutable_bias_filler()->set_type("constant");
  conv_param->mutable_bias_filler()->set_value(getenv_f("CK_IN_BIAS_CONST_VALUE", 1.1));

  caffe::ConvolutionLayer<float> layer(layer_param);

  measure_setup([&]() {
    layer.SetUp(inputs, outputs);
  });

  float *in_data = get_random_raw_data<float>(in_shape);
  print_input_raw_data(in_data, in_shape);
  memcpy(input->mutable_cpu_data(), in_data, in_shape.data_count() * sizeof(float));
  delete[] in_data;

  measure_test([&]() {
    layer.Forward(inputs, outputs);
  });

  Shape out_shape;
  out_shape.num = output->num();
  out_shape.channels = output->channels();
  out_shape.height = output->height();
  out_shape.width = output->width();
  float *out_data = new float[out_shape.data_count()];
  memcpy(out_data, output->data()->cpu_data(), out_shape.data_count() * sizeof(float));
  print_output_raw_data(out_data, out_shape);
  dump_output_raw_data(out_data, out_shape);
  delete[] out_data;

  delete input;
  delete output;

  finish_test();
}

} // namespace Caffe
} // namespace CK

#endif // CK_NNTEST_CAFFE_CONV_H
