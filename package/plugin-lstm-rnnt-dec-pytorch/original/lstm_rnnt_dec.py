import torch
import os
from torch import nn
from torch.nn import Parameter
from typing import Optional, Tuple

checkpoint_dir = "RNNT_CHECKPOINT"

class PluginLstmRnntDec(torch.nn.Module):
    def __init__(self):
        super().__init__()

        print("---------------------------------------")
        print("LOADING RNNT LSTM DEC: ORIGINAL PYTORCH")
        print("---------------------------------------")

        model = torch.load(os.path.join(checkpoint_dir,"rnnt.pt"), map_location="cpu")

        self.lstm = nn.LSTM(input_size=320,
            hidden_size=320,
            num_layers=2,
            dropout=0.0,
        )

        self.lstm.weight_ih_l0 = Parameter(model['state_dict']['prediction.dec_rnn.lstm.weight_ih_l0'])
        self.lstm.weight_hh_l0 = Parameter(model['state_dict']['prediction.dec_rnn.lstm.weight_hh_l0'])
        self.lstm.bias_ih_l0   = Parameter(model['state_dict']['prediction.dec_rnn.lstm.bias_ih_l0'])
        self.lstm.bias_hh_l0   = Parameter(model['state_dict']['prediction.dec_rnn.lstm.bias_hh_l0'])
        self.lstm.weight_ih_l1 = Parameter(model['state_dict']['prediction.dec_rnn.lstm.weight_ih_l1'])
        self.lstm.weight_hh_l1 = Parameter(model['state_dict']['prediction.dec_rnn.lstm.weight_hh_l1'])
        self.lstm.bias_ih_l1   = Parameter(model['state_dict']['prediction.dec_rnn.lstm.bias_ih_l1'])
        self.lstm.bias_hh_l1   = Parameter(model['state_dict']['prediction.dec_rnn.lstm.bias_hh_l1'])


    def forward(self, x: torch.Tensor, 
                init_states: Optional[Tuple[torch.Tensor, torch.Tensor]]=None
               ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:

        return self.lstm.forward(x, init_states)

