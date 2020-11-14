#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <time.h>

#include "model.h"

#define EMBEDDING_WIDTH _EMBEDDING_WIDTH*sizeof(float)
#define HIDDEN_WIDTH _HIDDEN_WIDTH*sizeof(float)
#define NUM_LAYERS _NUM_LAYERS
#define HIDDEN_STATE_SIZE HIDDEN_WIDTH*NUM_LAYERS


//===----------------------------------------------------------------------===//
//                 Wrapper code for executing a bundle
//===----------------------------------------------------------------------===//
/// Statically allocate memory for constant weights (model weights) and
/// initialize.
GLOW_MEM_ALIGN(MODEL_MEM_ALIGN)
uint8_t constantWeight[MODEL_CONSTANT_MEM_SIZE] = {
#include "model.weights.txt"
};

/// Statically allocate memory for mutable weights (model input/output data).
GLOW_MEM_ALIGN(MODEL_MEM_ALIGN)
uint8_t mutableWeight[MODEL_MUTABLE_MEM_SIZE];

/// Statically allocate memory for activations (model intermediate results).
GLOW_MEM_ALIGN(MODEL_MEM_ALIGN)
uint8_t activations[MODEL_ACTIVATIONS_MEM_SIZE];

/// Bundle input data absolute address.
uint8_t *inputAddr = GLOW_GET_ADDR(mutableWeight, MODEL_input);

/// Bundle hidden input data absolute address.
uint8_t *hiddenHInAddr = GLOW_GET_ADDR(mutableWeight, MODEL_h_0);
uint8_t *hiddenCInAddr = GLOW_GET_ADDR(mutableWeight, MODEL_c_0);

/// Bundle output data absolute address.
uint8_t *outputAddr = GLOW_GET_ADDR(mutableWeight, MODEL_output);

/// Bundle output data absolute address.
uint8_t *hiddenHOutAddr = GLOW_GET_ADDR(mutableWeight, MODEL_h_n);
uint8_t *hiddenCOutAddr = GLOW_GET_ADDR(mutableWeight, MODEL_c_n);


extern "C" {

int lstm(const float* in_data, const unsigned int len, const float* in_h_0, const float* in_c_0, float* out_data, float* out_h_n, float* out_c_n)
{
    if( in_h_0 != NULL && in_c_0 != NULL )
    {
        memcpy(hiddenHInAddr, in_h_0, HIDDEN_STATE_SIZE);
        memcpy(hiddenCInAddr, in_c_0, HIDDEN_STATE_SIZE);
    }
    else
    {
        memset(hiddenHInAddr,0,HIDDEN_STATE_SIZE);
        memset(hiddenCInAddr,0,HIDDEN_STATE_SIZE);
    }

    for( int i=0 ; i<len ; ++i)
    {
        unsigned int in_offset = i*EMBEDDING_WIDTH;
        unsigned int out_offset = i*HIDDEN_WIDTH;

        memcpy(inputAddr, &((uint8_t*)in_data)[in_offset], EMBEDDING_WIDTH);

        // Perform the computation.
        int errCode = model(constantWeight, mutableWeight, activations);
        if (errCode != GLOW_SUCCESS) {
            return errCode;
        }
        
        memcpy(&((uint8_t*)out_data)[out_offset], outputAddr, HIDDEN_WIDTH);
        memcpy(hiddenHInAddr, hiddenHOutAddr, HIDDEN_STATE_SIZE);
        memcpy(hiddenCInAddr, hiddenCOutAddr, HIDDEN_STATE_SIZE);
    }

    if( out_h_n != NULL && out_c_n != NULL )
    {
        memcpy(out_h_n, hiddenHOutAddr, HIDDEN_STATE_SIZE);
        memcpy(out_c_n, hiddenCOutAddr, HIDDEN_STATE_SIZE);
    }

    return GLOW_SUCCESS;
}

} //end extern "C"


