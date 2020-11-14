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

void run_squeezenet() {
  std::string data_path; /* Path to the trainable data */
  std::string image;     /* Image data */
  std::string label;     /* Label data */

  auto target_hint        = get_target_hint();
  auto convolution_method = get_convolution_method();

  GRAPH(graph, "SqueezeNetV1");

#if defined(ARMCL_18_05_PLUS)
  #define SUB_GRAPH(var_name) SubStream var_name(graph)
#else
  #define SUB_GRAPH(var_name) SubGraph var_name
#endif

  auto get_expand_fire_node = [&](const std::string &data_path, std::string &&param_path, unsigned int expand1_filt,
                                   unsigned int expand3_filt) -> BranchLayer {
    std::string total_path = "/cnn_data/squeezenet_v1.0_model/" + param_path + "_";
    SUB_GRAPH(i_a);
    i_a << ConvolutionLayer(
          1U, 1U, expand1_filt,
          get_weights_accessor(data_path, total_path + "expand1x1_w.npy"),
          get_weights_accessor(data_path, total_path + "expand1x1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU));

    SUB_GRAPH(i_b);
    i_b << ConvolutionLayer(
          3U, 3U, expand3_filt,
          get_weights_accessor(data_path, total_path + "expand3x3_w.npy"),
          get_weights_accessor(data_path, total_path + "expand3x3_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU));

    return BranchLayer(BranchMergeMethod::DEPTH_CONCATENATE, std::move(i_a), std::move(i_b));
  };

  xopenme_clock_start(X_TIMER_SETUP);
  graph << target_hint
        << convolution_method
        << make_input_layer(image, 224U, 224U, 3U, { 122.68f, 116.67f, 104.01f })
        << ConvolutionLayer(
          7U, 7U, 96U,
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/conv1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/conv1_b.npy"),
          PadStrideInfo(2, 2, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(2, 2, 0, 0, DimensionRoundingType::CEIL)))
        << ConvolutionLayer(
          1U, 1U, 16U,
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire2_squeeze1x1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire2_squeeze1x1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << get_expand_fire_node(data_path, "fire2", 64U, 64U)
        << ConvolutionLayer(
          1U, 1U, 16U,
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire3_squeeze1x1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire3_squeeze1x1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << get_expand_fire_node(data_path, "fire3", 64U, 64U)
        << ConvolutionLayer(
          1U, 1U, 32U,
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire4_squeeze1x1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire4_squeeze1x1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << get_expand_fire_node(data_path, "fire4", 128U, 128U)
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(2, 2, 0, 0, DimensionRoundingType::CEIL)))
        << ConvolutionLayer(
          1U, 1U, 32U,
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire5_squeeze1x1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire5_squeeze1x1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << get_expand_fire_node(data_path, "fire5", 128U, 128U)
        << ConvolutionLayer(
          1U, 1U, 48U,
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire6_squeeze1x1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire6_squeeze1x1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << get_expand_fire_node(data_path, "fire6", 192U, 192U)
        << ConvolutionLayer(
          1U, 1U, 48U,
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire7_squeeze1x1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire7_squeeze1x1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << get_expand_fire_node(data_path, "fire7", 192U, 192U)
        << ConvolutionLayer(
          1U, 1U, 64U,
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire8_squeeze1x1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire8_squeeze1x1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << get_expand_fire_node(data_path, "fire8", 256U, 256U)
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(2, 2, 0, 0, DimensionRoundingType::CEIL)))
        << ConvolutionLayer(
          1U, 1U, 64U,
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire9_squeeze1x1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/fire9_squeeze1x1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << get_expand_fire_node(data_path, "fire9", 256U, 256U)
        << ConvolutionLayer(
          1U, 1U, 1000U,
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/conv10_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/squeezenet_v1.0_model/conv10_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << PoolingLayer(PoolingLayerInfo(PoolingType::AVG))
        << FlattenLayer()
        << SoftmaxLayer()
        << make_output_layer(label);

#if defined(ARMCL_18_05_PLUS)
        // Finalize graph
        GraphConfig config {};
        graph.finalize(target_hint, config);
#endif

  xopenme_clock_end(X_TIMER_SETUP);

  xopenme_clock_start(X_TIMER_TEST);
  graph.run();
  xopenme_clock_end(X_TIMER_TEST);
}

