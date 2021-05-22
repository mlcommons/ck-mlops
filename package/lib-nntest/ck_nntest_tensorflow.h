/*
 * Copyright (c) 2017 cTuning foundation.
 * See CK COPYRIGHT.txt for copyright details.
 *
 * See CK LICENSE for licensing details.
 * See CK COPYRIGHT for copyright details.
 */

#ifndef CK_NNTEST_TENSORFLOW_H
#define CK_NNTEST_TENSORFLOW_H

#include "tensorflow/cc/client/client_session.h"
#include "tensorflow/cc/ops/nn_ops.h"
#include "tensorflow/core/util/stat_summarizer.h"

#include "ck_nntest_common.h"

namespace CK {
namespace TF {

// This is based on method StatSummarizer::ProcessStepStats()
// CK-TOOLS/<tensorflow_dir>/obj/tensorflow/tensorflow/core/util/stat_summarizer.cc
inline float get_node_time_ms(const tensorflow::StepStats &step_stats, const char *node_name) {
  tensorflow::int64 curr_total_us = 0;
  for (const auto &ds : step_stats.dev_stats()) {
    // We have several records for the node, see output of print_all_stat() for details.
    // E.g. for "my_softmax" these are: my_softmax/_0__cf__0, _retval_my_softmax_0_0.
    // Not sure whether should we take both times or only the first.
    for (const auto &ns : ds.node_stats()) {
      if (ns.node_name().find(node_name) != std::string::npos) {
        curr_total_us += ns.all_end_rel_micros();
      }
    }
  }
  return float(curr_total_us) / 1000.0;
}

inline void print_all_stat(const tensorflow::StepStats &step_stats) {
  tensorflow::StatSummarizerOptions stat_options;
  tensorflow::StatSummarizer stat_summarizer(stat_options);
  stat_summarizer.ProcessStepStats(step_stats);
  stat_summarizer.PrintStepStats();
}

inline const char *get_padding_scheme_str(int scheme) {
  assert(scheme == PADDING_SCHEME_SAME || scheme == PADDING_SCHEME_VALID);
  return scheme == PADDING_SCHEME_SAME ? "SAME" : "VALID";
}

inline CK::Shape get_tensor_shape(const tensorflow::Tensor &tensor) {
  CK::Shape shape;
  shape.num = tensor.shape().dim_size(0);
  shape.height = tensor.shape().dim_size(1);
  shape.width = tensor.shape().dim_size(2);
  shape.channels = tensor.shape().dim_size(3);
  return shape;
}

inline tensorflow::TensorShape get_tensor_shape(const CK::Shape &shape) {
  // cast here to prevent compiler warnings
  return tensorflow::TensorShape({
    static_cast<tensorflow::int64>(shape.num),
    static_cast<tensorflow::int64>(shape.height),
    static_cast<tensorflow::int64>(shape.width),
    static_cast<tensorflow::int64>(shape.channels)
  });
}

template <typename TData>
inline void set_tensor_data(tensorflow::Tensor &tensor, TData *data, CK::Shape &shape) {
  memcpy(tensor.flat<TData>().data(), data, shape.data_count() * sizeof(TData));
}

template <typename TData>
inline TData *get_tensor_data(const tensorflow::Tensor &tensor, CK::Shape &shape) {
  int data_count = shape.data_count();
  TData *data = new TData[data_count];
  memcpy(data, tensor.flat<TData>().data(), data_count * sizeof(TData));
  return data;
}

inline void process_metadata(const tensorflow::RunMetadata &run_metadata, const char *node_name) {
  assert(run_metadata.has_step_stats());
  const tensorflow::StepStats &step_stats = run_metadata.step_stats();
  if (CK::getenv_i("CK_PRINT_TF_STAT", 0) != 0)
    print_all_stat(step_stats);
  float op_duration = get_node_time_ms(step_stats, node_name);
  printf("TensorFlow measured time for node '%s': %f\n", node_name, op_duration);
  store_test_time(op_duration);
}

struct PoolingParams {
  int kernel;
  int stride;
  const char *pad_scheme;
};

inline PoolingParams get_pooling_params_from_env(int default_kernel,
                                                 int default_stride,
                                                 int default_pad_scheme) {
  PoolingParams params;
  params.kernel = getenv_i("CK_POOL_KERNEL", default_kernel);
  params.stride = getenv_i("CK_POOL_STRIDE", default_stride);
  int pool_pad = getenv_i("CK_POOL_PAD_SCHEME", default_pad_scheme);
  params.pad_scheme = get_padding_scheme_str(pool_pad);
  printf("Pooling params: kernel=%d, stride=%d, pad_scheme=%d(%s)\n",
         params.kernel, params.stride, pool_pad, params.pad_scheme);
  return params;
}

} // namespace TF
} // namespace CK

#endif // CK_NNTEST_TENSORFLOW_H
