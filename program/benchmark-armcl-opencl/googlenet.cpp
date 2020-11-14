/*
 * Copyright (c) 2017-2018 ARM Limited.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include "benchmark-common.h"

#if defined(ARMCL_18_05_PLUS)
using namespace arm_compute::graph::frontend;
#endif

void run_googlenet() {
  std::string data_path; /* Path to the trainable data */
  std::string image;     /* Image data */
  std::string label;     /* Label data */

  auto target_hint        = get_target_hint();
  auto convolution_method = get_convolution_method();

  GRAPH(graph, "GoogleNet");

#if defined(ARMCL_18_05_PLUS)
  #define SUB_GRAPH(var_name) SubStream var_name(graph)
#else
  #define SUB_GRAPH(var_name) SubGraph var_name
#endif

  auto get_inception_node = [&](const std::string &data_path, std::string &&param_path,
                                 unsigned int a_filt,
                                 std::tuple<unsigned int, unsigned int> b_filters,
                                 std::tuple<unsigned int, unsigned int> c_filters,
                                 unsigned int d_filt) -> BranchLayer {
    std::string total_path = "/cnn_data/googlenet_model/" + param_path + "/" + param_path + "_";
    SUB_GRAPH(i_a);
    i_a << ConvolutionLayer(
          1U, 1U, a_filt,
          get_weights_accessor(data_path, total_path + "1x1_w.npy"),
          get_weights_accessor(data_path, total_path + "1x1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU));

    SUB_GRAPH(i_b);
    i_b << ConvolutionLayer(
          1U, 1U, std::get<0>(b_filters),
          get_weights_accessor(data_path, total_path + "3x3_reduce_w.npy"),
          get_weights_accessor(data_path, total_path + "3x3_reduce_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << ConvolutionLayer(
          3U, 3U, std::get<1>(b_filters),
          get_weights_accessor(data_path, total_path + "3x3_w.npy"),
          get_weights_accessor(data_path, total_path + "3x3_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU));

    SUB_GRAPH(i_c);
    i_c << ConvolutionLayer(
          1U, 1U, std::get<0>(c_filters),
          get_weights_accessor(data_path, total_path + "5x5_reduce_w.npy"),
          get_weights_accessor(data_path, total_path + "5x5_reduce_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << ConvolutionLayer(
          5U, 5U, std::get<1>(c_filters),
          get_weights_accessor(data_path, total_path + "5x5_w.npy"),
          get_weights_accessor(data_path, total_path + "5x5_b.npy"),
          PadStrideInfo(1, 1, 2, 2))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU));

    SUB_GRAPH(i_d);
    i_d << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(1, 1, 1, 1, DimensionRoundingType::CEIL)))
        << ConvolutionLayer(
          1U, 1U, d_filt,
          get_weights_accessor(data_path, total_path + "pool_proj_w.npy"),
          get_weights_accessor(data_path, total_path + "pool_proj_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU));

    return BranchLayer(BranchMergeMethod::DEPTH_CONCATENATE, std::move(i_a), std::move(i_b), std::move(i_c),
                       std::move(i_d));
  };

  xopenme_clock_start(X_TIMER_SETUP);
  graph << target_hint
        << convolution_method
        << make_input_layer(image, 224U, 224U, 3U, { 122.68f, 116.67f, 104.01f })
        << ConvolutionLayer(
          7U, 7U, 64U,
          get_weights_accessor(data_path, "/cnn_data/googlenet_model/conv1/conv1_7x7_s2_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/googlenet_model/conv1/conv1_7x7_s2_b.npy"),
          PadStrideInfo(2, 2, 3, 3))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(2, 2, 0, 0, DimensionRoundingType::CEIL)))
        << NormalizationLayer(NormalizationLayerInfo(NormType::CROSS_MAP, 5, 0.0001f, 0.75f))
        << ConvolutionLayer(
          1U, 1U, 64U,
          get_weights_accessor(data_path, "/cnn_data/googlenet_model/conv2/conv2_3x3_reduce_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/googlenet_model/conv2/conv2_3x3_reduce_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << ConvolutionLayer(
          3U, 3U, 192U,
          get_weights_accessor(data_path, "/cnn_data/googlenet_model/conv2/conv2_3x3_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/googlenet_model/conv2/conv2_3x3_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << NormalizationLayer(NormalizationLayerInfo(NormType::CROSS_MAP, 5, 0.0001f, 0.75f))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(2, 2, 0, 0, DimensionRoundingType::CEIL)))
        << get_inception_node(data_path, "inception_3a", 64, std::make_tuple(96U, 128U), std::make_tuple(16U, 32U), 32U)
        << get_inception_node(data_path, "inception_3b", 128, std::make_tuple(128U, 192U), std::make_tuple(32U, 96U), 64U)
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(2, 2, 0, 0, DimensionRoundingType::CEIL)))
        << get_inception_node(data_path, "inception_4a", 192, std::make_tuple(96U, 208U), std::make_tuple(16U, 48U), 64U)
        << get_inception_node(data_path, "inception_4b", 160, std::make_tuple(112U, 224U), std::make_tuple(24U, 64U), 64U)
        << get_inception_node(data_path, "inception_4c", 128, std::make_tuple(128U, 256U), std::make_tuple(24U, 64U), 64U)
        << get_inception_node(data_path, "inception_4d", 112, std::make_tuple(144U, 288U), std::make_tuple(32U, 64U), 64U)
        << get_inception_node(data_path, "inception_4e", 256, std::make_tuple(160U, 320U), std::make_tuple(32U, 128U), 128U)
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(2, 2, 0, 0, DimensionRoundingType::CEIL)))
        << get_inception_node(data_path, "inception_5a", 256, std::make_tuple(160U, 320U), std::make_tuple(32U, 128U), 128U)
        << get_inception_node(data_path, "inception_5b", 384, std::make_tuple(192U, 384U), std::make_tuple(48U, 128U), 128U)
        << PoolingLayer(PoolingLayerInfo(PoolingType::AVG, 7, PadStrideInfo(1, 1, 0, 0, DimensionRoundingType::CEIL)))
        << FullyConnectedLayer(
          1000U,
          get_weights_accessor(data_path, "/cnn_data/googlenet_model/loss3/loss3_classifier_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/googlenet_model/loss3/loss3_classifier_b.npy"))
        << SoftmaxLayer()
        << make_output_layer(label);

#if defined(ARMCL_18_05_PLUS)
        // Finalize graph
        GraphConfig config{};
        graph.finalize(target_hint, config);
#endif

  xopenme_clock_end(X_TIMER_SETUP);

  xopenme_clock_start(X_TIMER_TEST);
  graph.run();
  xopenme_clock_end(X_TIMER_TEST);
}

