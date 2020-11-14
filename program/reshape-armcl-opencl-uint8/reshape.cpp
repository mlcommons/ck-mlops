/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLReshapeLayer.h>

#include "arm_compute/core/PixelValue.h"

#include "ck_nntest_armcl.h"

using namespace CK;
using namespace CK::armcl;
using namespace arm_compute;

int main() {
  init_test();
  init_armcl();

  auto data_layout = get_data_layout_from_env();

  Shape in_shape = get_input_shape_from_env();

  Shape out_shape;
  out_shape.num =  in_shape.num;
  out_shape.height = getenv_i("CK_OUT_SHAPE_H", 1);
  out_shape.height = getenv_i("CK_OUT_SHAPE_H", 1);
  out_shape.width =  getenv_i("CK_OUT_SHAPE_W", 1);
  out_shape.channels = getenv_i("CK_OUT_SHAPE_C", 1);

  CLTensor input, output;
  CLReshapeLayer layer;

  const size_t in_shape_width = in_shape.width;
  const size_t in_shape_height = in_shape.height;
  const size_t in_shape_channels = in_shape.channels;
  const size_t in_shape_num = in_shape.num;

  const size_t out_shape_width = out_shape.width;
  const size_t out_shape_height = out_shape.height;
  const size_t out_shape_channels = out_shape.channels;
  const size_t out_shape_num = out_shape.num;

  measure_setup([&]() {
    TensorShape tensor_shape = to_tensor_shape(in_shape, data_layout);
    TensorShape shape_reshaped = to_tensor_shape(out_shape, data_layout);

    input.allocator()->init(make_tensor_info(tensor_shape, DataType::QASYMM8, data_layout));
    output.allocator()->init(make_tensor_info(shape_reshaped, DataType::QASYMM8, data_layout));

    layer.configure(&input, &output);

    input.allocator()->allocate();
    output.allocator()->allocate();

    uint8_t *in_data =  get_random_raw_data<uint8_t>(in_shape, 0, 255);
    print_input_raw_data(in_data, in_shape);
    if (data_layout == LAYOUT_NHWC)
      convert_data_layout_NCHW_to_NHWC(in_data, in_shape);
    copy_raw_data_to_tensor(&input, in_data, in_shape);
    delete[] in_data;
  });

  measure_test([&]() {
    layer.run();
    // Ensure that all OpenCL jobs have completed.
    CLScheduler::get().sync();
  });

  uint8_t *out_data = new uint8_t[out_shape.data_count()];
  copy_raw_data_from_tensor(&output, out_data, out_shape);
  if (data_layout == LAYOUT_NHWC)
    convert_data_layout_NHWC_to_NCHW(out_data, out_shape);
  print_output_raw_data(out_data, out_shape);
  dump_output_raw_data(out_data, out_shape);
  delete[] out_data;

  input.allocator()->free();
  output.allocator()->free();

  finish_test();
  return 0;
}
