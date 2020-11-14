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

  // reshape width <-> channels, otherwise get_flat_index(shape, id) doesn't work properly
  Shape shape = original_shape;
  shape.width = original_shape.channels;
  shape.channels = 1;

  CLTensor input, output;
  CLSoftmaxLayer layer;

  const float in_data_min = -1;
  const float in_data_max = 1;

  measure_setup([&]() {
    // Prepare input shape
    TensorShape tensor_shape(static_cast<size_t>(shape.width), 1u, static_cast<size_t>(shape.num));
    TensorInfo tensor_info(tensor_shape, 1, DataType::QASYMM8);
    init_quantization_info(tensor_info, in_data_min, in_data_max);
    input.allocator()->init(tensor_info);
    print_tensor_shape("Input  CL shape", &input);
    printf("scale=%f, offset=%d\n", input.info()->quantization_info().scale, input.info()->quantization_info().offset);

    // Prepare layer params
    const double beta = getenv_f("CK_BETA", 1);
    printf("Additional params: beta=%g\n", beta);

    // Configure layer
    layer.configure(&input, &output, beta);
    print_tensor_shape("Output CL shape", &output);
    printf("scale=%f, offset=%d\n", output.info()->quantization_info().scale, output.info()->quantization_info().offset);

    input.allocator()->allocate();
    output.allocator()->allocate();

    // Populate input buffer
    uint8_t *in_data = get_random_raw_data<uint8_t>(shape, 0, 255);
    print_input_raw_data(in_data, shape);
    copy_raw_data_to_tensor(&input, in_data, shape);
    delete[] in_data;
  });

  measure_test([&]() {
    layer.run();

    // Make sure all the OpenCL jobs are done executing
    CLScheduler::get().sync();
  });

  // Get and process output data
  uint8_t *out_data = new uint8_t[shape.data_count()];
  copy_raw_data_from_tensor(&output, out_data, shape);
  print_output_raw_data(out_data, shape);
  dump_output_raw_data(out_data, original_shape);
  delete[] out_data;

  input.allocator()->free();
  output.allocator()->free();

  finish_test();
  return 0;
}
