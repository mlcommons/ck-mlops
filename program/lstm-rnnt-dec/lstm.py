import os
import torch
import torch.nn as nn
import struct
import numpy as np
import json
from time import perf_counter
from pprint import pprint

from lstm_rnnt_dec import PluginLstmRnntDec

start_setup_time = perf_counter()

# Setup.
output_bin = os.environ.get('CK_OUT_RAW_DATA', 'tmp-ck-output.bin')
output_json = output_bin.replace('bin', 'json')

dataset_path = os.environ.get('CK_DATASET_PATH', '')

dataset_prefix = os.environ.get('CK_LSTM_DATASET_PREFIX', 'sample')

logit_count = os.environ.get('CK_LSTM_LOGIT_COUNT', '1')

op_id = os.environ.get('CK_LSTM_OP_ID', '')
sample_id = os.environ.get('CK_LSTM_SAMPLE_ID', '0').zfill(6)

layers = int(os.environ.get('CK_LSTM_LAYERS', '2'))
hidden_width = int(os.environ.get('CK_LSTM_HIDDEN_WIDTH', '320'))
input_width = int(os.environ.get('CK_LSTM_INPUT_WIDTH', '320'))

logit_count = int(os.environ.get('CK_LSTM_LOGIT_COUNT', '128'))
batch_size = int(os.environ.get('CK_LSTM_BATCH_SIZE', '1'))

dropout = float(os.environ.get('CK_LSTM_DROPOUT', '0.0'))

rnd_seed = int(os.environ.get('CK_SEED', '42'))
rng = np.random.RandomState(rnd_seed)

print_in_tensor = os.environ.get('CK_PRINT_IN_TENSOR', 'no') in [ 'yes', 'YES', 'ON', 'on', '1' ]
print_out_tensor = os.environ.get('CK_PRINT_OUT_TENSOR', 'no') in [ 'yes', 'YES', 'ON', 'on', '1' ]

sample_file = os.path.join(dataset_path, '{}{}-DEC0000.pt'.format(dataset_path, dataset_prefix))

sizeof_float32 = 4

# LOAD LSTM

lstm = PluginLstmRnntDec()

# LOAD DATA
if os.path.exists(sample_file):

    input_data = []
    for i in range(logit_count):
        sample_file = os.path.join(dataset_path, '{}{}-DEC{}.pt'.format(dataset_path, dataset_prefix, str(i).zfill(4)))
        input_data.append(torch.load(sample_file))

else:
    # Generate random input data
    input_data = []
    for i in range(logit_count):
        input_x = rng.randn(1, batch_size, input_width).astype(np.float32)
        input_x = torch.from_numpy(input_x)
        input_h = rng.randn(2, batch_size, hidden_width).astype(np.float32)
        input_h = torch.from_numpy(input_h)
        input_c = rng.randn(2, batch_size, hidden_width).astype(np.float32)
        input_c = torch.from_numpy(input_c)
        input_data.append([input_x,(input_h,input_c)])

if print_in_tensor:
    print("Input:")
    pprint(input_data)
    print("")

finish_setup_time = perf_counter()

# RUN THE TEST
output = torch.zeros([logit_count,1,hidden_width])
for i in range(logit_count):
    outx, _ = lstm(input_data[i][0], input_data[i][1])
    output[i:i+1]=outx

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
