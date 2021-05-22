/*
 * See CK LICENSE for licensing details.
 * See CK COPYRIGHT for copyright details.
 */

#ifndef __ARM_COMPUTE_LIBRARY_BENCHMARK_ALEXNET_H__
#define __ARM_COMPUTE_LIBRARY_BENCHMARK_ALEXNET_H__

// Headers under ${CK_ENV_LIB_ACL_INCLUDE}.
#include "arm_compute/core/Helpers.h"
#include "arm_compute/core/Types.h"
#include "arm_compute/runtime/NEON/functions/NEActivationLayer.h"
#include "arm_compute/runtime/NEON/functions/NEConvolutionLayer.h"
#include "arm_compute/runtime/NEON/functions/NEFullyConnectedLayer.h"
#include "arm_compute/runtime/NEON/functions/NENormalizationLayer.h"
#include "arm_compute/runtime/NEON/functions/NEPoolingLayer.h"
#include "arm_compute/runtime/NEON/functions/NESoftmaxLayer.h"
#include "arm_compute/runtime/SubTensor.h"
#include "arm_compute/runtime/Tensor.h"
#include "arm_compute/runtime/TensorAllocator.h"

// Headers under ${CK_ENV_LIB_ACL_SRC}.
#include "tests/NEON/Helper.h"
#include "tests/NEON/NEAccessor.h"
#include "tests/TensorLibrary.h"
#include "tests/model_objects/AlexNet.h"
#include "utils/Utils.h"

using namespace arm_compute;
using namespace arm_compute::utils;
using namespace arm_compute::test;
using namespace arm_compute::test::neon;

int main(int argc, char* argv[])
{
    // Init input image.
    PPMLoader ppm;
    Image image;
    if (argc < 2)
    {
        // Print help.
        std::cout << "Usage: " << argv[0] << " [input.ppm]\n\n";
        std::cout << "No input provided, creating a dummy 227x227 image ...\n";
        // Initialize the dimensions and format.
        image.allocator()->init(TensorInfo(227, 227, Format::U8));
    }
    else
    {
        const char* image_path = argv[1];
        std::cout << "Opening \'" << image_path << "\' ...\n\n";
        ppm.open(image_path);
        // Initialize the format.
        ppm.init_image(image, Format::U8);
    }
    image.allocator()->allocate();

    // Init AlexNet model.
    const unsigned int batches            = static_cast<unsigned int>(1);
    const bool         weights_transposed = true;

    model_objects::AlexNet<
        ITensor,
        Tensor,
        SubTensor,
        NEAccessor,
        NEActivationLayer,
        NEConvolutionLayer,
        NEFullyConnectedLayer,
        NENormalizationLayer,
        NEPoolingLayer,
        NESoftmaxLayer,
        DataType::F32
    >alexnet{};

    // Set up.
    alexnet.init_weights(batches, weights_transposed);
    alexnet.build();
    alexnet.allocate();

    // FIXME: references arm_compute::test::library.
    //alexnet.fill_random();

    // Run.
    alexnet.run();

    // Tear down.
    alexnet.clear();
    
    return 0;
}

#endif //__ARM_COMPUTE_LIBRARY_BENCHMARK_ALEXNET_H__
