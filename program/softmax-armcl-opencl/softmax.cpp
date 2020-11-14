/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLSoftmaxLayer.h>

#include "ck_nntest_armcl.h"

using namespace CK;
using namespace CK::armcl;
using namespace arm_compute;

int main() {
  init_test();
  init_armcl();

  Shape original_shape = get_input_shape_from_env();
  assert(original_shape.width == 1 && original_shape.height == 1);

  // Reshape width <-> channels, otherwise get_flat_index(shape, id) does not work properly.
  Shape shape = original_shape;
  shape.width = original_shape.channels;
  shape.channels = 1;

  CLTensor input, output;
  CLSoftmaxLayer layer;

  measure_setup([&]() {
    // Arm Compute Library only supports 1D softmax. This single dimension should be passed as width.
    TensorShape tensor_shape(static_cast<uint>(shape.width), static_cast<uint>(shape.num), static_cast<uint>(shape.height));
    input.allocator()->init(TensorInfo(tensor_shape, Format::F32));
    output.allocator()->init(TensorInfo(tensor_shape, Format::F32));

    layer.configure(&input, &output);

    input.allocator()->allocate();
    output.allocator()->allocate();

    float *in_data = get_random_raw_data<float>(shape);
    print_input_raw_data(in_data, shape);
    copy_raw_data_to_tensor(&input, in_data, shape);
    delete[] in_data;
  });

  measure_test([&]() {
    layer.run();
    // Ensure that all OpenCL jobs have completed.
    CLScheduler::get().sync();
  });

  float *out_data = new float[shape.data_count()];
  copy_raw_data_from_tensor(&output, out_data, shape);
  print_output_raw_data(out_data, shape);

  // Dump output using the original shape.
  dump_output_raw_data(out_data, original_shape);
  delete[] out_data;

  input.allocator()->free();
  output.allocator()->free();

  finish_test();
  return 0;
}
