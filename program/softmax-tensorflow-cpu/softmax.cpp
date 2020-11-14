/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include "ck_nntest_tensorflow.h"

using namespace CK;
using namespace CK::TF;
using namespace tensorflow;
using namespace tensorflow::ops;

int main() {
  init_test();

  Scope root = Scope::NewRootScope();

  CK::Shape shape = get_input_shape_from_env();
  assert(shape.width == 1 && shape.height == 1);

  // Prepare input data
  Tensor input(DT_FLOAT, TensorShape({shape.num, shape.channels}));
  float *in_data = get_random_raw_data<float>(shape);
  print_input_raw_data(in_data, shape);
  memcpy(input.flat<float>().data(), in_data, shape.data_count() * sizeof(float));
  delete[] in_data;

  // Prepare operation
  std::vector<Tensor> outputs;
  const char *test_node_name = "my_softmax";
  Softmax softmax(root.WithOpName(test_node_name), input);

  // Prepare measurement
  RunOptions run_options;
  run_options.set_trace_level(RunOptions::FULL_TRACE);
  RunMetadata run_metadata;

  // Run test
  measure_test([&]() {
    ClientSession session(root);
    auto result = session.Run(run_options, {}, {softmax}, {}, &outputs, &run_metadata);
    TF_CHECK_OK(result);
  });

  // Get output data
  float *out_data = new float[shape.data_count()];
  memcpy(out_data, outputs[0].flat<float>().data(), shape.data_count() * sizeof(float));
  print_output_raw_data(out_data, shape);
  dump_output_raw_data(out_data, shape);
  delete[] out_data;

  process_metadata(run_metadata, test_node_name);

  finish_test();
  return 0;
}
