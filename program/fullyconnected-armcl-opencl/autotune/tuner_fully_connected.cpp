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
 * OUT OF OR IN CONNEuCTIOlN WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
#include "tuner_fully_connected.h"

#include "arm_compute/core/CL/ICLKernel.h"
#include "arm_compute/runtime/CL/CLScheduler.h"

#include <chrono>
#include <limits>
#include <string>

using namespace arm_compute;

CLTuner_FullyConnected::CLTuner_FullyConnected()
  : _lws_table() {
}

#if defined(ARMCL_18_05_PLUS)
void CLTuner_FullyConnected::tune_kernel_dynamic(ICLKernel &kernel) {
  ARM_COMPUTE_UNUSED(kernel);
}

void CLTuner_FullyConnected::tune_kernel_static(ICLKernel &kernel)
#else
void CLTuner_FullyConnected::tune_kernel(ICLKernel &kernel)
#endif
{
  // Get the configuration ID from the kernel
  const std::string &config_id = kernel.config_id();

  // Check if we need to find the Optimal LWS. If config_id is equal to default_config_id, the kernel does not require to be tuned
  if(config_id != arm_compute::default_config_id) {
    auto p = _lws_table.find(config_id);

    if(p == _lws_table.end()) {
      // Find the optimal LWS for the kernel
      cl::NDRange opt_lws = find_optimal_lws(kernel);

      // Insert the optimal LWS in the table
      _lws_table.emplace(config_id, opt_lws);

      // Set the LWS hint
      kernel.set_lws_hint(opt_lws);
    }
    else {
      // Set the LWS hint
      kernel.set_lws_hint(p->second);
    }
  }
}

cl::NDRange CLTuner_FullyConnected::find_optimal_lws(ICLKernel &kernel) {
  cl::CommandQueue q = CLScheduler::get().queue();

  double min_exec_time = std::numeric_limits<double>::max();

  cl::NDRange opt_lws = cl::NDRange(1, 1, 1);
  {
    const int y = 1;
    const int z = 1;
    // Ensure at least one run with the default lws by finishing with invalid x=385.
    for(int x = 1; x <= 385; ++x) {
      cl::NDRange lws_test = cl::NDRange(x, y, z);

      // Set the LWS hint
      kernel.set_lws_hint(lws_test);

      auto t_start = std::chrono::high_resolution_clock::now();

      // Run the kernel with the specified LWS if valid
      kernel.run(kernel.window(), q);

      CLScheduler::get().sync();

      auto t_stop = std::chrono::high_resolution_clock::now();

      std::chrono::duration<double, std::nano> fp_nano = t_stop - t_start;

      // Check the execution time
      if(fp_nano.count() < min_exec_time) {
        min_exec_time = fp_nano.count();
        opt_lws       = cl::NDRange(x, y, z);
      }
    }
  }

  return opt_lws;
}

void CLTuner_FullyConnected::import_lws_table(const std::unordered_map<std::string, cl::NDRange> &lws_table) {
  _lws_table.clear();
  _lws_table = lws_table;
}

const std::unordered_map<std::string, cl::NDRange> &CLTuner_FullyConnected::export_lws_table() {
  return _lws_table;
}
