import os
import torch
import torch.nn as nn
import struct
import numpy as np
import json
from time import perf_counter
from pprint import pprint

start_setup_time = perf_counter()

# Setup.
output_bin = os.environ.get('CK_OUT_RAW_DATA', 'tmp-ck-output.bin')
output_json = output_bin.replace('bin', 'json')

dataset_path = os.environ.get('CK_DATASET_PATH', '')

weights_prefix = os.environ.get('CK_LSTM_WEIGHTS_PREFIX', 'weights')
dataset_prefix = os.environ.get('CK_LSTM_DATASET_PREFIX', 'sample')

op_id = os.environ.get('CK_LSTM_OP_ID', '')
sample_id = os.environ.get('CK_LSTM_SAMPLE_ID', '0').zfill(6)

layers = int(os.environ.get('CK_LSTM_LAYERS', '1'))
hidden_width = int(os.environ.get('CK_LSTM_HIDDEN_WIDTH', '1024'))
input_width = int(os.environ.get('CK_LSTM_INPUT_WIDTH', '240'))

logit_count = int(os.environ.get('CK_LSTM_LOGIT_COUNT', '128'))
batch_size = int(os.environ.get('CK_LSTM_BATCH_SIZE', '1'))

dropout = float(os.environ.get('CK_LSTM_DROPOUT', '0.0'))

rnd_seed = int(os.environ.get('CK_SEED', '42'))
rng = np.random.RandomState(rnd_seed)

print_in_tensor = os.environ.get('CK_PRINT_IN_TENSOR', 'no') in [ 'yes', 'YES', 'ON', 'on', '1' ]
print_out_tensor = os.environ.get('CK_PRINT_OUT_TENSOR', 'no') in [ 'yes', 'YES', 'ON', 'on', '1' ]

sample_file  = os.path.join(dataset_path, '{}{}-{}-{}.x'.format(dataset_path, dataset_prefix, op_id, sample_id))

sizeof_float32 = 4

# LOAD LSTM
weights_file = os.path.join(dataset_path, '{}{}-{}.W'.format(dataset_path, weights_prefix, op_id))

if os.path.exists(weights_file):
    # Create LSTM with available weights
    lstm = torch.load(weights_file)
else:
    # Create LSTM initialised with random data
    lstm = nn.LSTM(input_size=input_width, hidden_size=hidden_width, num_layers=layers, dropout=dropout)

    width = input_width
    for i in range(layers):
        weights_ih_layer_i = rng.randn(4*hidden_width, width).astype(np.float32)
        weights_hh_layer_i = rng.randn(4*hidden_width, hidden_width).astype(np.float32)
        lstm.all_weights[i][0].data = torch.from_numpy(weights_ih_layer_i)
        lstm.all_weights[i][1].data = torch.from_numpy(weights_hh_layer_i)

        bias_hh_layer_i = rng.randn(4*hidden_width).astype(np.float32)
        bias_ih_layer_i = rng.randn(4*hidden_width).astype(np.float32)
        lstm.all_weights[i][2].data = torch.from_numpy(bias_ih_layer_i)
        lstm.all_weights[i][3].data = torch.from_numpy(bias_hh_layer_i)
        width = hidden_width

# LOAD DATA
if os.path.exists(sample_file):
    # Load input data from file
    input_data = torch.load(sample_file)
    assert input_data.size()[2] == input_width
else:
    # Generate random input data
    input_data = rng.randn(logit_count, batch_size, input_width).astype(np.float32)
    input_data = torch.from_numpy(input_data)

if print_in_tensor:
    print("Input:")
    pprint(input_data)
    print("")

logit_count, _, _ = input_data.size()

finish_setup_time = perf_counter()

# RUN THE TEST
output, _ = lstm(input_data, None)

finish_lstm_time = perf_counter()

# Print output as tensor.
if print_out_tensor:
    print("LSTM Output:")
    pprint(output)

# Convert output to flat list.
output_list = output.flatten().tolist()

# Dump output as binary.
with open(output_bin, 'wb') as output_file:
    output_file.write( struct.pack('f'*len(output_list), *output_list) )

# Dump output as JSON.
with open(output_json, 'w') as output_file:
    output_file.write( json.dumps(output_list, indent=2) )

# Dump timing and misc info.
height, batch, width = output.size()

timer_json = 'tmp-ck-timer.json'
with open(timer_json, 'w') as output_file:
    timer = {
        "execution_time": (finish_lstm_time - start_setup_time),
        "run_time_state": {
            "input_width": input_width,
            "hidden_width": hidden_width,
            "num_layers": layers,
            "logit_count": logit_count,
            "out_shape_N": batch,
            "out_shape_C": 1,
            "out_shape_H": height,
            "out_shape_W": width,
            "rnd_seed": rnd_seed,
            "data_bits": sizeof_float32*8,
            "time_setup": (finish_setup_time - start_setup_time),
            "time_test": (finish_lstm_time - finish_setup_time)
        }
    }
    output_file.write( json.dumps(timer, indent=2) )
