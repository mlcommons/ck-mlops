import os
import torch
import argparse

from lstm_rnnt_dec import PluginLstmRnntDec

def parse_args():
    parser = argparse.ArgumentParser(description='PyTorch to ONNX')
    parser.add_argument("--dest", default=None, type=str,
                        required=True, help='destination filename')
    parser.add_argument("--input_size", default=None, type=int)
    parser.add_argument("--hidden_size", default=None, type=int)
    parser.add_argument("--layers", default=None, type=int)
    return parser.parse_args()

def main(args):

    model = PluginLstmRnntDec()

    x = torch.randn([1,1,args.input_size])
    h = torch.randn(args.layers, 1, args.hidden_size)
    c = torch.randn(args.layers, 1, args.hidden_size)

    o = torch.randn([1,1,args.hidden_size])
    hn = torch.randn(args.layers, 1, args.hidden_size)
    cn = torch.randn(args.layers, 1, args.hidden_size)

    torch.onnx.export(model, (x,(h, c)),
                      args.dest,
                      opset_version=9,
                      input_names=['input', 'h_0', 'c_0'],
                      output_names=['output', 'h_n', 'c_n'],
                      dynamic_axes = {'input': {0: 'batch'}, 'output': {0: 'batch'}},
                      example_outputs = (o,(hn, cn)),
                      verbose=True
                  )

if __name__ == "__main__":
    args = parse_args()

    main(args)

