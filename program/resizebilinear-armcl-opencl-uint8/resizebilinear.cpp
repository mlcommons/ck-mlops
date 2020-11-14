/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * SPDX-License-Identifier: BSD-3-Clause.
 * See CK LICENSE.txt for licensing details.
 */

#include <arm_compute/runtime/CL/functions/CLScale.h>

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
  out_shape.width =  getenv_i("CK_OUT_SHAPE_W", 1);
  out_shape.channels = getenv_i("CK_OUT_SHAPE_C", 1);

  CLTensor input, output;
  CLScale layer;

  measure_setup([&]() {
    TensorShape tensor_shape = to_tensor_shape(in_shape, data_layout);
    TensorShape shape_scaled = to_tensor_shape(out_shape, data_layout);

    input.allocator()->init(make_tensor_info(tensor_shape, DataType::QASYMM8, data_layout));
    output.allocator()->init(make_tensor_info(shape_scaled, DataType::QASYMM8, data_layout));
    
    InterpolationPolicy policy = InterpolationPolicy::BILINEAR;
    BorderMode border_mode =
      BorderMode::CONSTANT;         // TODO Pass as CK param CK_RB_BORDER_MODE {UNDEFINED, CONSTANT, REPLICATE}
    uint8_t constant_border_value = getenv_i("CK_RB_BORDER_VALUE", 0);

    layer.configure(&input, &output, policy, border_mode, PixelValue(constant_border_value));

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
