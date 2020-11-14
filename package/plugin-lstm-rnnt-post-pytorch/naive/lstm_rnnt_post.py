import torch
import os
from torch import nn
from torch.nn import Parameter
from typing import Optional, Tuple
from lstm_naive import NaiveStackedLSTM

checkpoint_dir = "RNNT_CHECKPOINT"

class PluginLstmRnntPost(torch.nn.Module):
    def __init__(self):
        super().__init__()

        print("-------------------------------------")
        print("LOADING RNNT LSTM POST: NAIVE PYTORCH")
        print("-------------------------------------")

        model = torch.load(os.path.join(checkpoint_dir,"rnnt.pt"), map_location="cpu")

        weights = nn.LSTM(input_size=2048,
                          hidden_size=1024,
                          num_layers=3,
                          dropout=0.0)

        weights.weight_ih_l0 = Parameter(model['state_dict']['encoder.post_rnn.lstm.weight_ih_l0'])
        weights.weight_hh_l0 = Parameter(model['state_dict']['encoder.post_rnn.lstm.weight_hh_l0'])
        weights.bias_ih_l0   = Parameter(model['state_dict']['encoder.post_rnn.lstm.bias_ih_l0'])
        weights.bias_hh_l0   = Parameter(model['state_dict']['encoder.post_rnn.lstm.bias_hh_l0'])
        weights.weight_ih_l1 = Parameter(model['state_dict']['encoder.post_rnn.lstm.weight_ih_l1'])
        weights.weight_hh_l1 = Parameter(model['state_dict']['encoder.post_rnn.lstm.weight_hh_l1'])
        weights.bias_ih_l1   = Parameter(model['state_dict']['encoder.post_rnn.lstm.bias_ih_l1'])
        weights.bias_hh_l1   = Parameter(model['state_dict']['encoder.post_rnn.lstm.bias_hh_l1'])
        weights.weight_ih_l2 = Parameter(model['state_dict']['encoder.post_rnn.lstm.weight_ih_l2'])
        weights.weight_hh_l2 = Parameter(model['state_dict']['encoder.post_rnn.lstm.weight_hh_l2'])
        weights.bias_ih_l2   = Parameter(model['state_dict']['encoder.post_rnn.lstm.bias_ih_l2'])
        weights.bias_hh_l2   = Parameter(model['state_dict']['encoder.post_rnn.lstm.bias_hh_l2'])

        self.lstm = NaiveStackedLSTM(2048, 1024, 3, 0.0)
        self.lstm.set_weights(weights)

    def forward(self, x: torch.Tensor, 
                init_states: Optional[Tuple[torch.Tensor, torch.Tensor]]=None
               ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:

        return self.lstm.forward(x, init_states)

