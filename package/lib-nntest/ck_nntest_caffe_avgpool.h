/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * See CK LICENSE for licensing details.
 * See CK COPYRIGHT for copyright details.
 */

#ifndef CK_NNTEST_CAFFE_AVGPOOL_H
#define CK_NNTEST_CAFFE_AVGPOOL_H

#include <caffe/blob.hpp>
#include <caffe/layers/pooling_layer.hpp>

#include "ck_nntest_common.h"

typedef caffe::Blob<float> FloatBlob;

namespace CK {
namespace Caffe {

inline void test_avgpool() {
  init_test();

  Shape in_shape = get_input_shape_from_env(1, 1, 7, 7);

  FloatBlob *input = new FloatBlob(
    in_shape.num, in_shape.channels, in_shape.height, in_shape.width);
  std::vector<FloatBlob *> inputs;
  inputs.push_back(input);

  FloatBlob *output = new FloatBlob();
  std::vector<FloatBlob *> outputs;
  outputs.push_back(output);

  caffe::LayerParameter layer_param;
  caffe::PoolingParameter *pooling_param = layer_param.mutable_pooling_param();
  int pool_kernel = getenv_i("CK_POOL_KERNEL", 7);
  int pool_stride = getenv_i("CK_POOL_STRIDE", 1);
  int pool_pad = getenv_i("CK_POOL_PAD", 0);
  printf("Pooling params: kernel=%d, stride=%d, padding=%d\n", pool_kernel, pool_stride, pool_pad);
  pooling_param->set_kernel_h(pool_kernel);
  pooling_param->set_kernel_w(pool_kernel);
  pooling_param->set_stride_h(pool_stride);
  pooling_param->set_stride_w(pool_stride);
  pooling_param->set_pad_h(pool_pad);
  pooling_param->set_pad_w(pool_pad);
  pooling_param->set_pool(caffe::PoolingParameter_PoolMethod_AVE);
  caffe::PoolingLayer<float> layer(layer_param);

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

#endif // CK_NNTEST_CAFFE_AVGPOOL_H
