/*
 * Copyright (c) 2017 ARM Limited.
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

void run_vgg16() {
  std::string data_path; /* Path to the trainable data */
  std::string image;     /* Image data */
  std::string label;     /* Label data */

  auto target_hint        = get_target_hint();
  auto convolution_method = get_convolution_method();
  
  GRAPH(graph, "VGG16");
  xopenme_clock_start(X_TIMER_SETUP);
  graph << target_hint
        << convolution_method
        << make_input_layer(image, 224U, 224U, 3U, { 123.68f, 116.779f, 103.939f })
        // Layer 1
        << ConvolutionLayer(
          3U, 3U, 64U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv1_1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv1_1_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 2
        << ConvolutionLayer(
          3U, 3U, 64U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv1_2_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv1_2_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 2, PadStrideInfo(2, 2, 0, 0)))
        // Layer 3
        << ConvolutionLayer(
          3U, 3U, 128U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv2_1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv2_1_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 4
        << ConvolutionLayer(
          3U, 3U, 128U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv2_2_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv2_2_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 2, PadStrideInfo(2, 2, 0, 0)))
        // Layer 5
        << ConvolutionLayer(
          3U, 3U, 256U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv3_1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv3_1_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 6
        << ConvolutionLayer(
          3U, 3U, 256U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv3_2_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv3_2_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 7
        << ConvolutionLayer(
          3U, 3U, 256U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv3_3_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv3_3_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 2, PadStrideInfo(2, 2, 0, 0)))
        // Layer 8
        << ConvolutionLayer(
          3U, 3U, 512U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv4_1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv4_1_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 9
        << ConvolutionLayer(
          3U, 3U, 512U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv4_2_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv4_2_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 10
        << ConvolutionLayer(
          3U, 3U, 512U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv4_3_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv4_3_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 2, PadStrideInfo(2, 2, 0, 0)))
        // Layer 11
        << ConvolutionLayer(
          3U, 3U, 512U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv5_1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv5_1_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 12
        << ConvolutionLayer(
          3U, 3U, 512U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv5_2_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv5_2_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 13
        << ConvolutionLayer(
          3U, 3U, 512U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv5_3_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/conv5_3_b.npy"),
          PadStrideInfo(1, 1, 1, 1))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 2, PadStrideInfo(2, 2, 0, 0)))
        // Layer 14
        << FullyConnectedLayer(
          4096U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/fc6_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/fc6_b.npy"))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 15
        << FullyConnectedLayer(
          4096U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/fc7_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/fc7_b.npy"))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        // Layer 16
        << FullyConnectedLayer(
          1000U,
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/fc8_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/vgg16_model/fc8_b.npy"))
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

