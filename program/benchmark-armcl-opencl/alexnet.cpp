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

void run_alexnet() {
  std::string data_path; /* Path to the trainable data */
  std::string image;     /* Image data */
  std::string label;     /* Label data */

  auto target_hint        = get_target_hint();
  auto convolution_method = get_convolution_method();

  GRAPH(graph, "AlexNet");
  xopenme_clock_start(X_TIMER_SETUP);
  graph << target_hint
        << convolution_method
        << make_input_layer(image, 227U, 227U, 3U, { 122.68f, 116.67f, 104.01f })
        // Layer 1
        << ConvolutionLayer(
          11U, 11U, 96U,
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/conv1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/conv1_b.npy"),
          PadStrideInfo(4, 4, 0, 0))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << NormalizationLayer(NormalizationLayerInfo(NormType::CROSS_MAP, 5, 0.0001f, 0.75f))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(2, 2, 0, 0)))
        // Layer 2
        << ConvolutionLayer(
          5U, 5U, 256U,
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/conv2_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/conv2_b.npy"),
          PadStrideInfo(1, 1, 2, 2), 2)
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << NormalizationLayer(NormalizationLayerInfo(NormType::CROSS_MAP, 5, 0.0001f, 0.75f))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(2, 2, 0, 0)))
        // Layer 3
        << ConvolutionLayer(
          3U, 3U, 384U,
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/conv3_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/conv3_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 4
        << ConvolutionLayer(
          3U, 3U, 384U,
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/conv4_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/conv4_b.npy"),
          PadStrideInfo(1, 1, 1, 1), 2)
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 5
        << ConvolutionLayer(
          3U, 3U, 256U,
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/conv5_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/conv5_b.npy"),
          PadStrideInfo(1, 1, 1, 1), 2)
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 3, PadStrideInfo(2, 2, 0, 0)))
        // Layer 6
        << FullyConnectedLayer(
          4096U,
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/fc6_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/fc6_b.npy"))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 7
        << FullyConnectedLayer(
          4096U,
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/fc7_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/fc7_b.npy"))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 8
        << FullyConnectedLayer(
          1000U,
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/fc8_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/alexnet_model/fc8_b.npy"))
        // Softmax
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

