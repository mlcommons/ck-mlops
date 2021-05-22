/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * See CK LICENSE for licensing details.
 * See CK COPYRIGHT for copyright details.
 */

#ifndef CK_NNTEST_CAFFE_SOFTMAX_H
#define CK_NNTEST_CAFFE_SOFTMAX_H

#include <caffe/blob.hpp>
#include <caffe/layers/softmax_layer.hpp>

#include "ck_nntest_common.h"

typedef caffe::Blob<float> FloatBlob;

namespace CK {
namespace Caffe {

inline void test_softmax() {
  init_test();

  Shape shape = get_input_shape_from_env();
  assert(shape.width == 1 && shape.height == 1);

  FloatBlob *input = new FloatBlob(
    shape.num, shape.channels, shape.height, shape.width);
  std::vector<FloatBlob *> inputs;
  inputs.push_back(input);

  FloatBlob *output = new FloatBlob();
  std::vector<FloatBlob *> outputs;
  outputs.push_back(output);

  caffe::LayerParameter layer_param;
  layer_param.mutable_softmax_param()->set_axis(1); // axis 1 is the 'channels' axis (see 'input' init above)
  caffe::SoftmaxLayer<float> layer(layer_param);

  measure_setup([&]() {
    layer.SetUp(inputs, outputs);
  });

  // Prepare input data
  float *in_data = get_random_raw_data<float>(shape);
  print_input_raw_data(in_data, shape);
  memcpy(input->mutable_cpu_data(), in_data, shape.data_count() * sizeof(float));
  delete[] in_data;

  measure_test([&]() {
    layer.Forward(inputs, outputs);
  });

  // Get output data
  float *out_data = new float[shape.data_count()];
  memcpy(out_data, output->data()->cpu_data(), shape.data_count() * sizeof(float));
  print_output_raw_data(out_data, shape);
  dump_output_raw_data(out_data, shape);
  delete[] out_data;

  delete input;
  delete output;

  finish_test();
}

} // namespace Caffe
} // namespace CK

#endif // CK_NNTEST_CAFFE_SOFTMAX_H
