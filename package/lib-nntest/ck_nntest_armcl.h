/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
 */

#ifndef CK_NNTEST_ARMCL_H
#define CK_NNTEST_ARMCL_H

#include <arm_compute/runtime/CL/CLScheduler.h>
#include <arm_compute/runtime/CL/CLTensor.h>
#include <arm_compute/runtime/CL/CLTuner.h>
#if defined(ARMCL_18_05_PLUS)
#include <arm_compute/runtime/CL/tuners/BifrostTuner.h>
#endif

#include "ck_nntest_common.h"

namespace CK {
namespace armcl {

enum CKDataLayout {
  LAYOUT_NCHW,
  LAYOUT_NHWC,
};

void printf_callback(const char *buffer, unsigned int len, size_t complete, void *user_data) {
  printf("%.*s", len, buffer);
}

inline void set_kernel_path() {
  const char *kernel_path = getenv("CK_ENV_LIB_ARMCL_CL_KERNELS");
  if (kernel_path) {
    printf("Kernel path: %s\n", kernel_path);
    arm_compute::CLKernelLibrary::get().set_kernel_path(kernel_path);
  }
}

inline void init_armcl(arm_compute::ICLTuner *cl_tuner = nullptr) {
  cl_context_properties properties[] = {
    CL_PRINTF_CALLBACK_ARM, reinterpret_cast<cl_context_properties>(printf_callback),
    CL_PRINTF_BUFFERSIZE_ARM, static_cast<cl_context_properties>(0x100000),
    CL_CONTEXT_PLATFORM, reinterpret_cast<cl_context_properties>(cl::Platform::get()()),
    0
  };
  cl::Context::setDefault(cl::Context(CL_DEVICE_TYPE_DEFAULT, properties));

  arm_compute::CLScheduler::get().default_init(cl_tuner);

  // Should be called after initialization
  set_kernel_path();
}

using TunerPtr = std::unique_ptr<arm_compute::ICLTuner>;

template <typename TCustomTuner>
TunerPtr get_lws_tuner() {
  auto tuner_type = getenv("CK_LWS_TUNER_TYPE");

  if (!tuner_type || strcmp(tuner_type, "NONE") == 0)
    return TunerPtr();

  if (strcmp(tuner_type, "CUSTOM") == 0) {
    printf("INFO: Custom tuner selected\n");
    return TunerPtr(new TCustomTuner());
  }

  if (strcmp(tuner_type, "DEFAULT") == 0) {
    printf("INFO: Tuner selected: CLTuner\n");
    return TunerPtr(new arm_compute::CLTuner());
  }
    
  if (strcmp(tuner_type, "BIFROST") == 0) {
#if defined(ARMCL_18_05_PLUS)
    printf("INFO: Tuner selected: BifrostTuner\n");
    auto device = cl::Device::getDefault();
    auto gpu_target = arm_compute::get_target_from_device(device);
    auto gpu_arch = arm_compute::get_arch_from_target(gpu_target);
    if (gpu_arch != arm_compute::GPUTarget::BIFROST) {
      printf("WARNING: BifrostTuner selected for non-Bifrost architecture.\n");
    }
    return TunerPtr(new arm_compute::tuners::BifrostTuner());
#else
    printf("WARNING: BifrostTuner is only available for ArmCL v18.05 and later. "
           "Default CLTuner will be used instead.\n");
    printf("INFO: Tuner selected: CLTuner\n");
    return TunerPtr(new arm_compute::CLTuner());
#endif
  }

  printf("WARNING: Unknown tuner type: %s\n", tuner_type);
  return TunerPtr();
}

inline int get_flat_index(const Shape &shape, const arm_compute::Coordinates &id, CKDataLayout data_layout) {
  const int n = id[3];
  const int c = data_layout == LAYOUT_NCHW ? id[2] : id[0];
  const int h = data_layout == LAYOUT_NCHW ? id[1] : id[2];
  const int w = data_layout == LAYOUT_NCHW ? id[0] : id[1];
  return n * (shape.width * shape.height * shape.channels) +
         c * (shape.width * shape.height) +
         h * shape.width +
         w;
}

inline arm_compute::TensorShape tensor_info_to_shape(const arm_compute::TensorInfo *info) {
  arm_compute::TensorShape shape;
  for (int dim = 0; dim < info->num_dimensions(); dim++) {
    shape.set(dim, info->dimension(dim));
  }
  return shape;
}

// ArmCL stores dimensions as
// Layout NCHW:      [N C H W]
// Dimension index:  [3 2 1 0]
// Layout NHWC:      [N H W C]
inline arm_compute::TensorShape to_tensor_shape(const Shape &shape, CKDataLayout data_layout) {
  switch (data_layout) {
    case LAYOUT_NCHW:
      return arm_compute::TensorShape(
               static_cast<size_t>(shape.width),
               static_cast<size_t>(shape.height),
               static_cast<size_t>(shape.channels),
               static_cast<size_t>(shape.num));
    case LAYOUT_NHWC:
      return arm_compute::TensorShape(
               static_cast<size_t>(shape.channels),
               static_cast<size_t>(shape.width),
               static_cast<size_t>(shape.height),
               static_cast<size_t>(shape.num));
  }
  return arm_compute::TensorShape();
}

inline Shape to_ck_shape(const arm_compute::TensorInfo *info, CKDataLayout data_layout) {
  Shape shape;
  switch (data_layout) {
    case LAYOUT_NCHW:
      shape.width = info->dimension(0);
      shape.height = info->dimension(1);
      shape.channels = info->dimension(2);
      shape.num = info->dimension(3);
      break;
    case LAYOUT_NHWC:
      shape.channels = info->dimension(0);
      shape.width = info->dimension(1);
      shape.height = info->dimension(2);
      shape.num = info->dimension(3);
      break;
  }
  return shape;
}

inline CKDataLayout get_data_layout(arm_compute::CLTensor *tensor) {
#if defined(ARMCL_18_08_PLUS)
  return tensor->info()->data_layout() == arm_compute::DataLayout::NCHW ? LAYOUT_NCHW : LAYOUT_NHWC;
#else
  return LAYOUT_NCHW;
#endif
}

template <typename TData>
inline void copy_raw_data_to_tensor(arm_compute::CLTensor *tensor, TData *data, const Shape &shape) {
  auto data_layout = get_data_layout(tensor);
  arm_compute::Window window;
  window.use_tensor_dimensions(tensor_info_to_shape(tensor->info()));
  tensor->map();
  arm_compute::Iterator it(tensor, window);
  arm_compute::execute_window_loop(window, [&](const arm_compute::Coordinates & id) {
    *reinterpret_cast<TData *>(it.ptr()) = data[get_flat_index(shape, id, data_layout)];
  }, it);
  tensor->unmap();
}

template <typename TData>
inline void copy_raw_data_to_tensor(arm_compute::CLTensor *tensor, TData *data, int data_count) {
  assert(tensor->info()->tensor_shape().total_size() == data_count);
  arm_compute::Window window;
  window.use_tensor_dimensions(tensor_info_to_shape(tensor->info()));
  tensor->map();
  arm_compute::Iterator it(tensor, window);
  int index = 0;
  arm_compute::execute_window_loop(window, [&](const arm_compute::Coordinates & id) {
    *reinterpret_cast<TData *>(it.ptr()) = data[index++];
  }, it);
  tensor->unmap();
}

template <typename TData>
inline void copy_raw_data_from_tensor(arm_compute::CLTensor *tensor, TData *data, const Shape &shape) {
  auto data_layout = get_data_layout(tensor);
  arm_compute::Window window;
  window.use_tensor_dimensions(tensor_info_to_shape(tensor->info()));
  tensor->map();
  arm_compute::Iterator it(tensor, window);
  arm_compute::execute_window_loop(window, [&](const arm_compute::Coordinates & id) {
    data[get_flat_index(shape, id, data_layout)] = *reinterpret_cast<TData *>(it.ptr());
  }, it);
  tensor->unmap();
}

template <typename TData>
inline void copy_raw_data_from_tensor(arm_compute::CLTensor *tensor, TData *data, int data_count) {
  assert(tensor->info()->tensor_shape().total_size() == data_count);
  arm_compute::Window window;
  window.use_tensor_dimensions(tensor_info_to_shape(tensor->info()));
  tensor->map();
  arm_compute::Iterator it(tensor, window);
  int index = 0;
  arm_compute::execute_window_loop(window, [&](const arm_compute::Coordinates & id) {
    data[index++] = *reinterpret_cast<TData *>(it.ptr());
  }, it);
  tensor->unmap();
}

inline void print_tensor_shape(const char *header, const arm_compute::CLTensor *tensor) {
  auto info = tensor->info();
  printf("%s: num_dims=%d, ", header, static_cast<int>(info->num_dimensions()));
  for (size_t dim = 0; dim < info->num_dimensions(); dim++) {
    printf("dim[%d]=%d, ", static_cast<int>(dim), static_cast<int>(info->dimension(dim)));
  }
  printf("num_channels=%d\n", static_cast<int>(info->num_channels()));
}

inline void print_tensor_data(const char *header, arm_compute::CLTensor *tensor) {
  printf("%s:\n", header);
  tensor->map();
  tensor->print(std::cout);
  tensor->unmap();
}


#if 0
// FIXME: 'scale' used to be of type 'float', now of type 'std::vector<float>';
// 'offset' used to be of type 'int', now of type 'std::vector<int, std:allocator<int> >'.
inline void print_quantization_info(const char *header, const arm_compute::TensorInfo &info) {
  printf("Quantized %s: scale=%f, offset=%d\n", header, info.quantization_info().scale(), info.quantization_info().offset());
}
#endif

typedef ConvolutionParams PoolingParams;

inline PoolingParams get_pooling_params_from_env(int default_kernel,
                                                 int default_stride,
                                                 int default_pad) {
  PoolingParams params;
  params.kernel = static_cast<unsigned int>(getenv_i("CK_POOL_KERNEL", default_kernel));
  params.stride = static_cast<unsigned int>(getenv_i("CK_POOL_STRIDE", default_stride));
  params.pad = static_cast<unsigned int>(getenv_i("CK_POOL_PAD", default_pad));
  printf("Pooling params: kernel=%d, stride=%d, pad=%d\n",
         params.kernel, params.stride, params.pad);
  return params;
}

inline arm_compute::QuantizationInfo get_quantization_info(float min_value, float max_value) {
  assert(max_value > min_value);
  const float quant_min = 0;
  const float quant_max = 255;
  const float quant_range = quant_max - quant_min;
  const float scale = (max_value - min_value) / quant_range;
  const int offset = fmin(quant_max, fmax(quant_min, round(quant_min - min_value / scale)));
  return arm_compute::QuantizationInfo(scale, offset);
}

inline void init_quantization_info(arm_compute::TensorInfo &info, float min_value, float max_value) {
  info.set_quantization_info(get_quantization_info(min_value, max_value));
}

inline CKDataLayout get_data_layout_from_env() {
#if defined(ARMCL_18_08_PLUS)
  auto data_layout_str = getenv("CK_DATA_LAYOUT");

  if (!data_layout_str)
    return LAYOUT_NCHW;

  if (strcmp(data_layout_str, "NCHW") == 0)
    return LAYOUT_NCHW;

  if (strcmp(data_layout_str, "NHWC") == 0)
    return LAYOUT_NHWC;
    
  printf("WARNING: Unknown data layout: %s\n", data_layout_str);
#endif
  return LAYOUT_NCHW;
}

inline arm_compute::TensorInfo make_tensor_info(const arm_compute::TensorShape& tensor_shape,
                                                arm_compute::DataType data_type,
                                                CKDataLayout data_layout) {
  arm_compute::TensorInfo tensor_info(tensor_shape, 1, data_type);

#if defined(ARMCL_18_08_PLUS)
  switch (data_layout) {
    case LAYOUT_NCHW:
      tensor_info.set_data_layout(arm_compute::DataLayout::NCHW);
      break;

    case LAYOUT_NHWC:
      tensor_info.set_data_layout(arm_compute::DataLayout::NHWC);
      break;
  }
#endif

  return tensor_info;
}

} // namespace armcl
} // namespace CK

#endif // CK_NNTEST_ARMCL_H
