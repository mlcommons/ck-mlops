import torch
import os
import numpy
from torch import nn
from torch.nn import Parameter
from enum import IntEnum
from typing import Optional, Tuple
import onnxruntime as rt

plugin_dir = "PLUGIN_DIR"

class PluginLstmRnntPost(torch.nn.Module):
    def __init__(self):
        super().__init__()

        print("----------------------------")
        print("LOADING RNNT LSTM POST: ONNX")
        print("----------------------------")

        onnx_file = os.path.join(plugin_dir,"model.onnx")
        with open(onnx_file, 'rb') as fp:
            model = fp.read()

        self.session = rt.InferenceSession(model)

        self.input  = self.session.get_inputs()[0].name
        self.h_0 = self.session.get_inputs()[1].name
        self.c_0 = self.session.get_inputs()[2].name
        self.input_type_x = self.session.get_inputs()[0].type
        self.input_type_h0 = self.session.get_inputs()[1].type
        self.input_type_c0 = self.session.get_inputs()[2].type
        self.input_shape_x = self.session.get_inputs()[0].shape
        self.input_shape_h0 = self.session.get_inputs()[1].shape
        self.input_shape_c0 = self.session.get_inputs()[2].shape

        self.output = self.session.get_outputs()[0].name
        self.h_n = self.session.get_outputs()[1].name
        self.c_n = self.session.get_outputs()[2].name
        self.output_shape_o = self.session.get_outputs()[0].shape
        self.output_shape_hn = self.session.get_outputs()[1].shape
        self.output_shape_cn = self.session.get_outputs()[2].shape

        self.zeros_h_0 = numpy.zeros(self.input_shape_h0, dtype=numpy.float32)
        self.zeros_c_0 = numpy.zeros(self.input_shape_c0, dtype=numpy.float32)

        print("input %s" % self.input, self.input_shape_x)
        print("input %s" % self.h_0, self.input_shape_h0)
        print("input %s" % self.c_0, self.input_shape_c0)
        print("output o", self.output_shape_o)
        print("output hn", self.output_shape_hn)
        print("output cn", self.output_shape_cn)


    def forward(self, x: torch.Tensor, 
                init_states: Optional[Tuple[torch.Tensor]]=None
               ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:

        # Convert the inputs to Numpy and float32
        xin = x.numpy().astype(numpy.float32)
        if init_states:
            h_0 = init_states[0].numpy().astype(numpy.float32)
            c_0 = init_states[1].numpy().astype(numpy.float32)
        else:
            h_0 = self.zeros_h_0
            c_0 = self.zeros_c_0

        res = self.session.run([self.output, self.h_n, self.c_n], {self.input: xin, self.h_0: h_0, self.c_0: c_0})

        result = torch.from_numpy(res[0])
        h_n = torch.from_numpy(res[1])
        c_n = torch.from_numpy(res[2])

        return result, (h_n, c_n)

