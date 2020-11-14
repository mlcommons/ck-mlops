/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLPoolingLayer.h>

#include "ck_nntest_armcl.h"

using namespace CK;
using namespace CK::armcl;
using namespace arm_compute;

#define DEFAULT_IN_N 1
#define DEFAULT_IN_C 1
#define DEFAULT_IN_H 7
#define DEFAULT_IN_W 7
#define DEFAULT_POOL_KERNEL 7
#define DEFAULT_POOL_STRIDE 1
#define DEFAULT_POOL_PAD 0

int main() {
  init_test();
  init_armcl();

  auto data_layout = get_data_layout_from_env();
  Shape in_shape = get_input_shape_from_env(DEFAULT_IN_N, DEFAULT_IN_C,
                                            DEFAULT_IN_H, DEFAULT_IN_W);

  CLTensor input, output;
  CLPoolingLayer layer;

  measure_setup([&]() {
    // Prepare input shape
    TensorShape native_in_shape = to_tensor_shape(in_shape, data_layout);
    input.allocator()->init(make_tensor_info(native_in_shape, DataType::F32, data_layout));

    // Prepare operation params
    PoolingParams pool_params = get_pooling_params_from_env(
                                  DEFAULT_POOL_KERNEL, DEFAULT_POOL_STRIDE, DEFAULT_POOL_PAD);
    bool exclude_padding = getenv_i("CK_EXCLUDE_PADDING", 0);
    printf("exclude_padding=%d\n", exclude_padding);
    PadStrideInfo pool_pad_stride(pool_params.stride, pool_params.stride,
                                  pool_params.pad, pool_params.pad);
    PoolingLayerInfo layer_info(PoolingType::AVG, pool_params.kernel, pool_pad_stride, exclude_padding);

    // Configure layer
    layer.configure(&input, &output, layer_info);
    print_tensor_shape("Configured CL shape", &output);

    input.allocator()->allocate();
    output.allocator()->allocate();

    // Populate input buffer
    float *in_data = get_random_raw_data<float>(in_shape);
    print_input_raw_data(in_data, in_shape);
    copy_raw_data_to_tensor(&input, in_data, in_shape);
    delete[] in_data;
  });

  measure_test([&]() {
    layer.run();

    // Make sure all the OpenCL jobs are done executing
    CLScheduler::get().sync();
  });

  // Get and process output data
  Shape out_shape = to_ck_shape(output.info(), data_layout);
  float *out_data = new float[out_shape.data_count()];
  copy_raw_data_from_tensor(&output, out_data, out_shape);
  print_output_raw_data(out_data, out_shape);
  dump_output_raw_data(out_data, out_shape);
  delete[] out_data;

  input.allocator()->free();
  output.allocator()->free();

  finish_test();
  return 0;
}
