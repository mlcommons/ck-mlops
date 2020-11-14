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

void run_lenet() {
  std::string data_path; /** Path to the trainable data */

  unsigned int batch_size = get_batch_size(); /** Number of images per batch */

  auto target_hint        = get_target_hint();
  auto convolution_method = get_convolution_method();

  GRAPH(graph, "LeNet");

  //conv1 << pool1 << conv2 << pool2 << fc1 << act1 << fc2 << smx
  xopenme_clock_start(X_TIMER_SETUP);
  graph << target_hint
        << convolution_method
#if defined(ARMCL_18_05_PLUS)
        << InputLayer(TensorDescriptor(TensorShape(28U, 28U, 1U, batch_size), DataType::F32), get_input_accessor(""))
#else
        << Tensor(TensorInfo(TensorShape(28U, 28U, 1U, batch_size), 1, DATATYPE), DummyAccessor())
#endif
        << ConvolutionLayer(
          5U, 5U, 20U,
          get_weights_accessor(data_path, "/cnn_data/lenet_model/conv1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/lenet_model/conv1_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 2, PadStrideInfo(2, 2, 0, 0)))
        << ConvolutionLayer(
          5U, 5U, 50U,
          get_weights_accessor(data_path, "/cnn_data/lenet_model/conv2_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/lenet_model/conv2_b.npy"),
          PadStrideInfo(1, 1, 0, 0))
        << PoolingLayer(PoolingLayerInfo(PoolingType::MAX, 2, PadStrideInfo(2, 2, 0, 0)))
        << FullyConnectedLayer(
          500U,
          get_weights_accessor(data_path, "/cnn_data/lenet_model/ip1_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/lenet_model/ip1_b.npy"))
        << ActivationLayer(ActivationLayerInfo(ActivationLayerInfo::ActivationFunction::RELU))
        << FullyConnectedLayer(
          10U,
          get_weights_accessor(data_path, "/cnn_data/lenet_model/ip2_w.npy"),
          get_weights_accessor(data_path, "/cnn_data/lenet_model/ip2_b.npy"))
        << SoftmaxLayer()
#if defined(ARMCL_18_05_PLUS)
        << OutputLayer(get_output_accessor(""));
#else
        << Tensor(DummyAccessor());
#endif

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

