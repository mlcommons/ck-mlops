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

#define DEFAULT_IN_N 1
#define DEFAULT_IN_C 1
#define DEFAULT_IN_H 7
#define DEFAULT_IN_W 7
#define DEFAULT_POOL_KERNEL 7
#define DEFAULT_POOL_STRIDE 1
#define DEFAULT_POOL_PAD 0

int main() {
  init_test();

  Scope root = Scope::NewRootScope();

  // Prepare input data
  CK::Shape in_shape = get_input_shape_from_env(DEFAULT_IN_N, DEFAULT_IN_C,
                                                DEFAULT_IN_H, DEFAULT_IN_W);
  float *in_data = get_random_raw_data<float>(in_shape);
  print_input_raw_data(in_data, in_shape);
  convert_data_layout_NCHW_to_NHWC(in_data, in_shape);
  Tensor input(DT_FLOAT, get_tensor_shape(in_shape));
  set_tensor_data(input, in_data, in_shape);
  delete[] in_data;

  // Prepare operation
  const char *test_node_name = "my_avgpool";
  PoolingParams pool_params = get_pooling_params_from_env(
                                DEFAULT_POOL_KERNEL, DEFAULT_POOL_STRIDE, PADDING_SCHEME_VALID);
  AvgPool avgpool(root.WithOpName(test_node_name),
                  input,
  {1, pool_params.kernel, pool_params.kernel, 1},
  {1, pool_params.stride, pool_params.stride, 1},
  pool_params.pad_scheme);

  // Prepare measurement
  RunOptions run_options;
  run_options.set_trace_level(RunOptions::FULL_TRACE);
  RunMetadata run_metadata;

  // Run test
  std::vector<Tensor> outputs;
  measure_test([&]() {
    ClientSession session(root);
    auto result = session.Run(run_options, {}, {avgpool}, {}, &outputs, &run_metadata);
    TF_CHECK_OK(result);
  });

  // Process output data
  const Tensor &output = outputs[0];
  CK::Shape out_shape = get_tensor_shape(output);
  float *out_data = get_tensor_data<float>(output, out_shape);
  convert_data_layout_NHWC_to_NCHW(out_data, out_shape);
  print_output_raw_data(out_data, out_shape);
  dump_output_raw_data(out_data, out_shape);
  delete[] out_data;

  process_metadata(run_metadata, test_node_name);

  finish_test();
  return 0;
}
