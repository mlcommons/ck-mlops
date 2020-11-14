import torch
import os
import numpy as np
from torch import nn
from typing import Optional, Tuple
import time

import ctypes
import numpy.ctypeslib as ctl

plugin_dir      = "PLUGIN_DIR"
embedding_width = int("EMBEDDING_WIDTH")
hidden_width    = int("HIDDEN_WIDTH")
num_layers      = int("NUM_LAYERS")

class PluginLstmRnntPost(torch.nn.Module):
    def __init__(self):
        super().__init__()

        print("----------------------------")
        print("LOADING RNNT LSTM POST: GLOW")
        print("----------------------------")

        self.libc = ctypes.CDLL(plugin_dir + "/model.so")
        self.lstm = self.libc.lstm

        self.lstm.argtypes = [ctl.ndpointer(np.float32, flags='aligned, c_contiguous'),
                              ctypes.c_int,
                              ctl.ndpointer(np.float32, flags='aligned, c_contiguous'),
                              ctl.ndpointer(np.float32, flags='aligned, c_contiguous'),
                              ctl.ndpointer(np.float32, flags='aligned, c_contiguous'),
                              ctl.ndpointer(np.float32, flags='aligned, c_contiguous'),
                              ctl.ndpointer(np.float32, flags='aligned, c_contiguous')]

        self.zeros_h_0 = np.zeros([num_layers,1,hidden_width], dtype=np.float32)
        self.zeros_c_0 = np.zeros([num_layers,1,hidden_width], dtype=np.float32)

    def forward(self, x: torch.Tensor, 
                init_states: Optional[Tuple[torch.Tensor]]=None
               ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:

        logits = x.size()[0]
        # Convert the inputs to Numpy, float32 and contiguous for C
        xin = x.numpy().astype(np.float32, order='C')
        if init_states:
            h_0 = init_states[0].numpy().astype(np.float32, order='C')
            c_0 = init_states[1].numpy().astype(np.float32, order='C')
        else:
            h_0 = self.zeros_h_0
            c_0 = self.zeros_c_0

        out = np.empty([logits,1,hidden_width], dtype=np.float32)
        h_n = np.empty([num_layers,1,hidden_width], dtype=np.float32)
        c_n = np.empty([num_layers,1,hidden_width], dtype=np.float32)

        self.lstm(xin, logits, h_0, c_0, out, h_n, c_n)

        out = torch.from_numpy(out)
        h_n = torch.from_numpy(h_n)
        c_n = torch.from_numpy(c_n)

        return out, (h_n, c_n)

