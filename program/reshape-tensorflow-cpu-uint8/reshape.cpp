/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include "ck_nntest_tensorflow.h"
#include "tensorflow/cc/ops/array_ops.h"

using namespace CK;
using namespace CK::TF;
using namespace tensorflow;
using namespace tensorflow::ops;

int main() {
  init_test();

  Scope root = Scope::NewRootScope();

  CK::Shape shape = get_input_shape_from_env();

  // Prepare input data
  Tensor input(DT_QUINT8, TensorShape({shape.num, shape.height, shape.width, shape.channels}));

  quint8 *in_data = get_random_raw_data<quint8>(shape, 0, 255);
  print_input_raw_data(in_data, shape);
  memcpy(input.flat<quint8>().data(), in_data, shape.data_count() * sizeof(quint8));
  delete[] in_data;

  CK::Shape out_shape;
  out_shape.num =  shape.num;
  out_shape.height = getenv_i("CK_OUT_SHAPE_H", 1);
  out_shape.width =  getenv_i("CK_OUT_SHAPE_W", 1);
  out_shape.channels = getenv_i("CK_OUT_SHAPE_C", 1);
  Tensor output(DT_QUINT8, TensorShape({out_shape.num, out_shape.height, out_shape.width, out_shape.channels}));

  // Prepare operation
  std::vector<Tensor> outputs;
  const char *test_node_name = "test_reshape";

  tensorflow::ops::Reshape reshape(root.WithOpName(test_node_name), input, ops::Shape(root.WithOpName("outShape"),
                                                                                      output));

  // Prepare measurement
  RunOptions run_options;
  run_options.set_trace_level(RunOptions::FULL_TRACE);
  RunMetadata run_metadata;

  // Run test
  measure_test([&]() {
    ClientSession session(root);
    auto result = session.Run(run_options, {}, {reshape}, {}, &outputs, &run_metadata);
    TF_CHECK_OK(result);
  });

  // Get output data
  quint8 *out_data = get_tensor_data<quint8>(output, out_shape);

  memcpy(out_data, outputs[0].flat<quint8>().data(), out_shape.data_count() * sizeof(quint8));
  print_output_raw_data(out_data, out_shape);
  dump_output_raw_data(out_data, out_shape);
  delete[] out_data;

  process_metadata(run_metadata, test_node_name);

  finish_test();
  return 0;
}
