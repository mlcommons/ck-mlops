/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * See CK LICENSE for licensing details.
 * See CK COPYRIGHT for copyright details.
 */

#ifndef CK_NNTEST_CAFFE_FC_H
#define CK_NNTEST_CAFFE_FC_H

#include <vector>

#include <caffe/blob.hpp>
#include <caffe/layers/inner_product_layer.hpp>
#include <caffe/filler.hpp>

#include "ck_nntest_common.h"

namespace CK {
namespace Caffe {


typedef caffe::Blob<float> FloatBlob;

inline void test_fc() {
  init_test();

  Shape in_shape = get_input_shape_from_env();

  FloatBlob *input = new FloatBlob(
    in_shape.num, in_shape.channels, in_shape.height, in_shape.width);
  std::vector<FloatBlob *> inputs;
  inputs.push_back(input);

  Shape out_shape;
  out_shape.num = in_shape.num;
  out_shape.channels = getenv_i("CK_OUT_SHAPE_C", 1);
  out_shape.width = 1;
  out_shape.height = 1;

  FloatBlob *output = new FloatBlob(in_shape.num, in_shape.channels, in_shape.height, in_shape.width);
  std::vector<FloatBlob *> outputs;
  outputs.push_back(output);


  caffe::LayerParameter layer_param;
  caffe::InnerProductParameter *inner_product_param = layer_param.mutable_inner_product_param();
  inner_product_param->set_num_output(out_shape.channels);
  inner_product_param->set_bias_term(true);

  inner_product_param->mutable_weight_filler()->set_type("constant"); // "uniform", "gaussian" available as well
  inner_product_param->mutable_weight_filler()->set_value(getenv_i("CK_IN_WEIGHTS_CONST_VALUE", 1));
  inner_product_param->mutable_bias_filler()->set_type("constant");   // "uniform", "gaussian" available as well
  inner_product_param->mutable_bias_filler()->set_min(0);
  inner_product_param->mutable_bias_filler()->set_max(getenv_i("CK_IN_BIAS_CONST_VALUE", 0));

  caffe::InnerProductLayer<float> layer(layer_param);

  measure_setup([&]() {
    layer.SetUp(inputs, outputs);
  });

  // Prepare input data
  float *in_data = get_random_raw_data<float>(in_shape);
  print_input_raw_data(in_data, in_shape);
  memcpy(input->mutable_cpu_data(), in_data, in_shape.data_count() * sizeof(float));
  delete[] in_data;

  measure_test([&]() {
    layer.Forward(inputs, outputs);
  });

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

#endif // CK_NNTEST_CAFFE_FC_H
