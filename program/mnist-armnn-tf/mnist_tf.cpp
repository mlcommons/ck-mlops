//
// Copyright © 2017 Arm Ltd. All rights reserved.
// See LICENSE file in the project root for full license information.
//

#include <stdlib.h>
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <memory>
#include <array>
#include <algorithm>
#include <sys/stat.h>
#include "armnn/ArmNN.hpp"
#include "armnn/Exceptions.hpp"
#include "armnn/Tensor.hpp"
#include "armnn/INetwork.hpp"
#include "armnnTfParser/ITfParser.hpp"

#include "mnist_loader.hpp"

/// Load an optional boolean value from the environment.
inline bool getenv_b(const char *name) {
    std::string value = getenv(name);

    return (value == "YES" || value == "yes" || value == "ON" || value == "on" || value == "1");
}


// Helper function to make input tensors
armnn::InputTensors MakeInputTensors(const std::pair<armnn::LayerBindingId,
    armnn::TensorInfo>& input,
    const void* inputTensorData)
{
    return { { input.first, armnn::ConstTensor(input.second, inputTensorData) } };
}

// Helper function to make output tensors
armnn::OutputTensors MakeOutputTensors(const std::pair<armnn::LayerBindingId,
    armnn::TensorInfo>& output,
    void* outputTensorData)
{
    return { { output.first, armnn::Tensor(output.second, outputTensorData) } };
}

int main(int argc, char** argv)
{
    bool use_neon                   = getenv_b("USE_NEON");
    bool use_opencl                 = getenv_b("USE_OPENCL");

    if (argc != 4) {
        std::cerr << "Usage: " << argv[0]
                  << " model image-directory file-number" << std::endl;
    return 1;
    }

    std::string model      = argv[1];
    std::string dataDir    = argv[2];
    std::string fileNumber = argv[3];

    struct stat info;
    if (stat(model.c_str(), &info) != 0) {
        printf("%s is not a file\n", model.c_str());
        return 1;
    }

    if (dataDir.back() != '/') dataDir.append("/");
    stat(dataDir.c_str(), &info);
    if(!(info.st_mode & S_IFDIR)) {
        printf("%s is not a directory\n", dataDir.c_str());
        return 1;
    }

    int testImageIndex = std::stoi(fileNumber.c_str());

    // Load a test image and its correct label
    std::unique_ptr<MnistImage> input = loadMnistImage(dataDir.c_str(), testImageIndex);
    if (input == nullptr)
        return 1;

    // Import the TensorFlow model. Note: use CreateNetworkFromBinaryFile for .pb files.
    armnnTfParser::ITfParserPtr parser = armnnTfParser::ITfParser::Create();
    armnn::INetworkPtr network = parser->CreateNetworkFromTextFile(model.c_str(),
                                                                   { {"Placeholder", {1, 784, 1, 1}} },
                                                                   { "Softmax" });

    // Find the binding points for the input and output nodes
    armnnTfParser::BindingPointInfo inputBindingInfo = parser->GetNetworkInputBindingInfo("Placeholder");
    armnnTfParser::BindingPointInfo outputBindingInfo = parser->GetNetworkOutputBindingInfo("Softmax");

    // Optimize the network for a specific runtime compute device, e.g. CpuAcc, GpuAcc
    std::vector<armnn::BackendId> optOptions = {armnn::Compute::CpuRef};
    if( use_neon && use_opencl) {
        optOptions = {armnn::Compute::CpuAcc, armnn::Compute::GpuAcc};
    } else if( use_neon ) {
        optOptions = {armnn::Compute::CpuAcc};
    } else if( use_opencl ) {
        optOptions = {armnn::Compute::GpuAcc};
    }
    armnn::IRuntime::CreationOptions options;
    armnn::IRuntimePtr runtime = armnn::IRuntime::Create(options);
    armnn::IOptimizedNetworkPtr optNet = armnn::Optimize(*network, optOptions, runtime->GetDeviceSpec());

    // Load the optimized network onto the runtime device
    armnn::NetworkId networkIdentifier;
    runtime->LoadNetwork(networkIdentifier, std::move(optNet));

    // Run a single inference on the test image
    std::array<float, 10> output;
    armnn::Status ret = runtime->EnqueueWorkload(networkIdentifier,
                                                 MakeInputTensors(inputBindingInfo, &input->image[0]),
                                                 MakeOutputTensors(outputBindingInfo, &output[0]));

    // Convert 1-hot output to an integer label and print
    int label = std::distance(output.begin(), std::max_element(output.begin(), output.end()));
    std::cout << "Predicted: " << label << std::endl;
    std::cout << "   Actual: " << input->label << std::endl;
    return 0;
}
