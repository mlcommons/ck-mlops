/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * See CK LICENSE for licensing details.
 * See CK COPYRIGHT for copyright details.
 */

#ifndef CK_NN_OPS_TEST_H
#define CK_NN_OPS_TEST_H

#include <xopenme.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <limits>
#include <utility>

enum {
  X_TIMER_SETUP,
  X_TIMER_TEST,

  X_TIMERS_COUNT
};

enum {
  X_VAR_OUT_N,
  X_VAR_OUT_C,
  X_VAR_OUT_H,
  X_VAR_OUT_W,
  X_VAR_IN_N,
  X_VAR_IN_C,
  X_VAR_IN_H,
  X_VAR_IN_W,
  X_VAR_SEED,
  X_VAR_BITS,
  X_VAR_TIME_SETUP,
  X_VAR_TIME_TEST,

  X_VAR_COUNT
};

namespace CK {

struct Shape {
  int num = 1;
  int channels = 1;
  int height = 1;
  int width = 1;

  static Shape make_nchw(int n, int c, int h, int w) {
    Shape ret;
    ret.num = n;
    ret.channels = c;
    ret.height = h;
    ret.width = w;
    return ret;
  }

  static Shape make_chw(int c, int h, int w) {
    return make_nchw(1, c, h, w);
  }

  int data_count() const {
    return num * channels * height * width;
  }

  int get_flat_index(int n, int c, int h, int w) const {
    return get_flat_index_nchw(n, c, h, w);
  }

  int get_flat_index_nchw(int n, int c, int h, int w) const {
    return ((n * channels + c) * height + h) * width + w;
  }

  int get_flat_index_nhwc(int n, int h, int w, int c) const {
    return ((n * height + h) * width + w) * channels + c;
  }

  int get_flat_index_whcn(int w, int h, int c, int n) const {
    return ((w * height + h) * channels + c) * num + n;
  }
};

/**
 * Convolution and Pooling padding scheme.
 * Padding scheme is used by TensorFlow. See here:
 * https://www.tensorflow.org/api_guides/python/nn#Pooling
 * But Caffe and ArmCL use explicit padding in pixels instead.
 */
enum PaddingScheme {
  PADDING_SCHEME_SAME = 1,
  PADDING_SCHEME_VALID = 2
};

struct ConvolutionParams {
  unsigned int kernel;
  unsigned int stride;
  unsigned int pad;
};

inline int getenv_i(const char *name, int def) {
  return getenv(name) ? atoi(getenv(name)) : def;
}

inline double getenv_f(const char *name, double def) {
  return getenv(name) ? atof(getenv(name)) : def;
}

inline void store_value_i(int index, const char *name, int value) {
  char *json_name = new char[strlen(name) + 6];
  sprintf(json_name, "\"%s\":%%d", name);
  xopenme_add_var_i(index, json_name, value);
  delete[] json_name;
}

inline void store_value_f(int index, const char *name, float value) {
  char *json_name = new char[strlen(name) + 6];
  sprintf(json_name, "\"%s\":%%f", name);
  xopenme_add_var_f(index, json_name, value);
  delete[] json_name;
}

inline Shape get_input_shape_from_env(int default_num = 1,
                                      int default_channels = 3,
                                      int default_height = 1,
                                      int default_width = 1) {
  Shape shape;
  shape.num = getenv_i("CK_IN_SHAPE_N", default_num);
  shape.channels = getenv_i("CK_IN_SHAPE_C", default_channels);
  shape.height = getenv_i("CK_IN_SHAPE_H", default_height);
  shape.width = getenv_i("CK_IN_SHAPE_W", default_width);
  store_value_i(X_VAR_IN_N, "in_shape_N", shape.num);
  store_value_i(X_VAR_IN_C, "in_shape_C", shape.channels);
  store_value_i(X_VAR_IN_H, "in_shape_H", shape.height);
  store_value_i(X_VAR_IN_W, "in_shape_W", shape.width);
  printf("Input shape: num=%d, channels=%d, height=%d, width=%d\n",
         shape.num, shape.channels, shape.height, shape.width);
  return shape;
}

inline ConvolutionParams get_conv_params_from_env(int default_kernel,
                                                  int default_stride,
                                                  int default_pad) {
  ConvolutionParams params{};
  params.kernel = static_cast<unsigned int>(getenv_i("CK_CONV_KERNEL", default_kernel));
  params.stride = static_cast<unsigned int>(getenv_i("CK_CONV_STRIDE", default_stride));
  params.pad = static_cast<unsigned int>(getenv_i("CK_CONV_PAD", default_pad));
  printf("Convolution params: kernel=%d, stride=%d, pad=%d\n",
         params.kernel, params.stride, params.pad);
  return params;
}

/// Returns float random value in range 0..1
inline float get_random_f() {
  return static_cast<float>(rand() % 1000001) / 1000000.0;
}

template <typename TData>
inline std::pair<Shape, TData *> get_data_with_padding(const Shape &source_shape,
                                                       const TData *source_data,
                                                       int pad_size,
                                                       const TData &pad_value) {
  Shape padded_shape = source_shape;
  padded_shape.height += 2 * pad_size;
  padded_shape.width += 2 * pad_size;
  TData *padded_data = new TData[padded_shape.data_count()];
  for (int n = 0; n < padded_shape.num; ++n) {
    for (int c = 0; c < padded_shape.channels; ++c) {
      for (int h = 0; h < padded_shape.height; ++h) {
        if (h < pad_size || h >= padded_shape.height - pad_size) {
          for (int w = 0; w < padded_shape.width; ++w) {
            int index = padded_shape.get_flat_index_nchw(n, c, h, w);
            padded_data[index] = pad_value;
          }
        }
        else {
          for (int w = 0; w < padded_shape.width; ++w) {
            int index = padded_shape.get_flat_index_nchw(n, c, h, w);
            if (w < pad_size || w >= padded_shape.width - pad_size) {
              padded_data[index] = pad_value;
            }
            else {
              int source_index = source_shape.get_flat_index_nchw(n, c, h - pad_size, w - pad_size);
              padded_data[index] = source_data[source_index];
            }
          }
        }
      }
    }
  }
  return std::pair<Shape, TData *>(padded_shape, padded_data);
}

/// Returns array of random data populated with values in range min..max
template <typename TData>
inline TData *get_random_raw_data(const Shape &shape, TData min, TData max) {
  assert(max > min);
  float max_float = std::numeric_limits<float>::max();
  assert(min >= -max_float && min <= max_float);
  assert(max >= -max_float && max <= max_float);

  store_value_i(X_VAR_BITS, "data_bits", sizeof(TData) * 8);

  const int data_count = shape.data_count();
  TData *data = new TData[data_count];
  const double min_f = static_cast<double>(min);
  const double max_f = static_cast<double>(max);
  const float range_f = max_f - min_f;
  for (int i = 0; i < data_count; ++i)
    data[i] = static_cast<TData>(min_f + range_f * get_random_f());
  return data;
}

template <typename TData>
inline TData *get_random_raw_data(const Shape &shape) {
  store_value_i(X_VAR_BITS, "data_bits", sizeof(TData) * 8);

  const int rnd_max = 1000000;
  const int rnd_range = 2 * rnd_max + 1;
  const int data_count = shape.data_count();
  TData *data = new TData[data_count];
  for (int i = 0; i < data_count; ++i)
    data[i] = static_cast<TData>(-rnd_max + rand() % rnd_range) / static_cast<TData>(rnd_max);
  return data;
}

template <typename TData>
inline TData *get_const_raw_data(int data_count, const TData &value) {
  TData *data = new TData[data_count];
  for (int i = 0; i < data_count; ++i)
    data[i] = value;
  return data;
}

template <typename TData>
inline void print_raw_data(TData *data, const Shape &shape) {
  printf("-----------------------------------\n");
  printf("Shape (N*C*H*W): %d*%d*%d*%d\n",
         shape.num, shape.channels, shape.height, shape.width);
  for (int n = 0; n < shape.num; ++n) {
    for (int c = 0; c < shape.channels; ++c) {
      printf("N=%d, C=%d:\n", n, c);
      for (int h = 0; h < shape.height; ++h) {
        for (int w = 0; w < shape.width; ++w) {
          int index = shape.get_flat_index(n, c, h, w);
          printf("% 8g\t", static_cast<float>(data[index]));
        }
        printf("\n");
      }
    }
  }
  printf("-----------------------------------\n");
}

template <typename TData>
inline void log_raw_data(TData *data, const Shape &shape, const char *env_var, const char *title) {
  if (env_var && getenv_i(env_var, 0)) {
    if (title) {
      printf("%s:\n", title);
    }
    print_raw_data(data, shape);
  }
}

template <typename TData>
inline void print_input_raw_data(TData *data, const Shape &shape) {
  log_raw_data(data, shape, "CK_PRINT_IN_TENSOR", "INPUT");
}

template <typename TData>
inline void print_output_raw_data(TData *data, const Shape &shape) {
  log_raw_data(data, shape, "CK_PRINT_OUT_TENSOR", "OUTPUT");
}

template <typename TData>
inline void print_weights_raw_data(TData *data, const Shape &shape) {
  log_raw_data(data, shape, "CK_PRINT_WEIGHTS_TENSOR", "WEIGHTS");
}

template <typename TData>
inline void dump_output_raw_data(TData *data, const Shape &shape) {
  char *file_name = getenv("CK_OUT_RAW_DATA");
  if (!file_name) return;

  xopenme_dump_memory(file_name, data, shape.data_count() * sizeof(TData));

  store_value_i(X_VAR_OUT_N, "out_shape_N", shape.num);
  store_value_i(X_VAR_OUT_C, "out_shape_C", shape.channels);
  store_value_i(X_VAR_OUT_H, "out_shape_H", shape.height);
  store_value_i(X_VAR_OUT_W, "out_shape_W", shape.width);
}

template <typename TData>
inline void convert_data_layout_NCHW_to_NHWC(TData *data_nchw, const CK::Shape &shape) {
  TData *data_nhwc = new TData[shape.data_count()];
  for (int n = 0; n < shape.num; ++n) {
    for (int c = 0; c < shape.channels; ++c) {
      for (int h = 0; h < shape.height; ++h) {
        for (int w = 0; w < shape.width; ++w) {
          int index_nhwc = shape.get_flat_index_nhwc(n, h, w, c);
          int index_nchw = shape.get_flat_index_nchw(n, c, h, w);
          data_nhwc[index_nhwc] = data_nchw[index_nchw];
        }
      }
    }
  }
  memcpy(data_nchw, data_nhwc, shape.data_count() * sizeof(TData));
  delete[] data_nhwc;
}

template <typename TData>
inline void convert_data_layout_NHWC_to_NCHW(TData *data_nhwc, const CK::Shape &shape) {
  TData *data_nchw = new TData[shape.data_count()];
  for (int n = 0; n < shape.num; ++n) {
    for (int c = 0; c < shape.channels; ++c) {
      for (int h = 0; h < shape.height; ++h) {
        for (int w = 0; w < shape.width; ++w) {
          int index_nhwc = shape.get_flat_index_nhwc(n, h, w, c);
          int index_nchw = shape.get_flat_index_nchw(n, c, h, w);
          data_nchw[index_nchw] = data_nhwc[index_nhwc];
        }
      }
    }
  }
  memcpy(data_nhwc, data_nchw, shape.data_count() * sizeof(TData));
  delete[] data_nchw;
}

inline void init_test() {
  xopenme_init(X_TIMERS_COUNT, X_VAR_COUNT);

  int seed = getenv_i("CK_SEED", 42);
  store_value_i(X_VAR_SEED, "rnd_seed", seed);
  srand(static_cast<unsigned int>(seed));
}

inline void finish_test() {
  printf("time-%d, setup: %f\n", X_TIMER_SETUP, xopenme_get_timer(X_TIMER_SETUP));
  printf("time-%d, test:  %f\n", X_TIMER_TEST, xopenme_get_timer(X_TIMER_TEST));
  xopenme_dump_state();
  xopenme_finish();
}

template <typename L>
inline void do_measured(L &&lambda_function, int timerId) {
  xopenme_clock_start(timerId);
  lambda_function();
  xopenme_clock_end(timerId);
}

void store_setup_time(float time) {
  store_value_f(X_VAR_TIME_SETUP, "time_setup", time);
}

void store_test_time(float time) {
  store_value_f(X_VAR_TIME_TEST, "time_test", time);
}

template <typename L>
inline void measure_setup(L &&lambda_function) {
  do_measured(lambda_function, X_TIMER_SETUP);
  store_setup_time(xopenme_get_timer(X_TIMER_SETUP));
}

template <typename L>
inline void measure_test(L &&lambda_function) {
  do_measured(lambda_function, X_TIMER_TEST);
  store_test_time(xopenme_get_timer(X_TIMER_TEST));
}

template <typename TData>
inline void calc_data_range(TData *data, size_t data_count, TData *min, TData *max) {
  TData data_min = std::numeric_limits<TData>::max();
  TData data_max = std::numeric_limits<TData>::min();
  for (size_t i = 0; i < data_count; i++) {
    if (data_min > data[i]) data_min = data[i];
    if (data_max < data[i]) data_max = data[i];
  }
  *min = data_min;
  *max = data_max;
}

} // namespace CK

#endif // CK_NN_OPS_TEST_H
