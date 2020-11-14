import torch
from torch import nn
from torch.nn import Parameter
from enum import IntEnum
from typing import Optional, Tuple

plugin_dir = "PLUGIN_DIR"

class Dim(IntEnum):
    seq = 0
    batch = 1
    feature = 2


class NaiveLayerLSTM(torch.nn.Module):
    def __init__(self, input_sz: int, hidden_sz: int):
        super().__init__()
        self.input_size = input_sz
        self.hidden_size = hidden_sz
        # input gate
        self.W_ii = Parameter(torch.Tensor(input_sz, hidden_sz))
        self.W_hi = Parameter(torch.Tensor(hidden_sz, hidden_sz))
        self.b_ii = Parameter(torch.Tensor(hidden_sz))
        self.b_hi = Parameter(torch.Tensor(hidden_sz))
        # forget gate
        self.W_if = Parameter(torch.Tensor(input_sz, hidden_sz))
        self.W_hf = Parameter(torch.Tensor(hidden_sz, hidden_sz))
        self.b_if = Parameter(torch.Tensor(hidden_sz))
        self.b_hf = Parameter(torch.Tensor(hidden_sz))
        # cell gate
        self.W_ig = Parameter(torch.Tensor(input_sz, hidden_sz))
        self.W_hg = Parameter(torch.Tensor(hidden_sz, hidden_sz))
        self.b_ig = Parameter(torch.Tensor(hidden_sz))
        self.b_hg = Parameter(torch.Tensor(hidden_sz))
        # output gate
        self.W_io = Parameter(torch.Tensor(input_sz, hidden_sz))
        self.W_ho = Parameter(torch.Tensor(hidden_sz, hidden_sz))
        self.b_io = Parameter(torch.Tensor(hidden_sz))
        self.b_ho = Parameter(torch.Tensor(hidden_sz))

        self.h_t, self.c_t = torch.zeros(self.hidden_size), torch.zeros(self.hidden_size)

    def set_weights(self, weights):
        self.W_ii = Parameter(weights[0][0].transpose(0,1))
        self.W_if = Parameter(weights[0][1].transpose(0,1))
        self.W_ig = Parameter(weights[0][2].transpose(0,1))
        self.W_io = Parameter(weights[0][3].transpose(0,1))
        self.W_hi = Parameter(weights[1][0].transpose(0,1))
        self.W_hf = Parameter(weights[1][1].transpose(0,1))
        self.W_hg = Parameter(weights[1][2].transpose(0,1))
        self.W_ho = Parameter(weights[1][3].transpose(0,1))
        self.b_ii = Parameter(weights[2][0])
        self.b_if = Parameter(weights[2][1])
        self.b_ig = Parameter(weights[2][2])
        self.b_io = Parameter(weights[2][3])
        self.b_hi = Parameter(weights[3][0])
        self.b_hf = Parameter(weights[3][1])
        self.b_hg = Parameter(weights[3][2])
        self.b_ho = Parameter(weights[3][3])

    def set_states(self, x: torch.Tensor, 
                init_states: Optional[Tuple[torch.Tensor]]=None
               ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        if init_states is None:
            self.h_t, self.c_t = torch.zeros(self.hidden_size).to(x.device), torch.zeros(self.hidden_size).to(x.device)
        else:
            self.h_t, self.c_t = init_states

    def get_states(self):
            return self.h_t, self.c_t

    def forward(self, x_t: torch.Tensor) -> torch.Tensor:
        """Assumes x_t is of shape feature"""
        i_t = torch.sigmoid(x_t @ self.W_ii + self.b_ii + self.h_t @ self.W_hi + self.b_hi)
        f_t = torch.sigmoid(x_t @ self.W_if + self.b_if + self.h_t @ self.W_hf + self.b_hf)
        g_t = torch.tanh(x_t @ self.W_ig + self.b_ig + self.h_t @ self.W_hg + self.b_hg)
        o_t = torch.sigmoid(x_t @ self.W_io + self.b_io + self.h_t @ self.W_ho + self.b_ho)
        self.c_t = f_t * self.c_t + i_t * g_t
        self.h_t = o_t * torch.tanh(self.c_t)

        return self.h_t



class NaiveStackedLSTM(torch.nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size

        self.layers = [ NaiveLayerLSTM(input_size, hidden_size) ]

        for l in range(num_layers-1):
            self.layers.append( NaiveLayerLSTM(hidden_size, hidden_size) )

        self.layers = nn.ModuleList(self.layers)

        self.num_layers = num_layers

    def set_weights(self, ref):
        for l in range(len(self.layers)):
            weights = [ref.all_weights[l][0].data.chunk(4, 0), 
                       ref.all_weights[l][1].data.chunk(4, 0),
                       ref.all_weights[l][2].data.chunk(4, 0),
                       ref.all_weights[l][3].data.chunk(4, 0)]
            self.layers[l].set_weights(weights)


    def forward(self, x: torch.Tensor, 
                init_states: Optional[Tuple[torch.Tensor, torch.Tensor]]=None
               ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:

        """Initialize the hidden states"""
        for l in range(self.num_layers):
            state = None if init_states is None else (init_states[0][l], init_states[1][l])
            self.layers[l].set_states(x, state)
  
        """Assumes x is of shape (sequence, batch, feature)"""
        seq_sz, bs, _ = x.size()
        hidden_seq = []
        for t in range(seq_sz): # iterate over the time steps
            x_t = x[t, :, :]
            for layer in self.layers:
                x_t = layer(x_t)
            hidden_seq.append(x_t.unsqueeze(Dim.batch))
        hidden_seq = torch.cat(hidden_seq, dim=Dim.batch)
        # reshape from shape (sequence, batch, feature) to (batch, sequence, feature)
        hidden_seq = hidden_seq.transpose(Dim.batch, Dim.seq).contiguous()

        """Retrieve hidden states"""
        h_layers = []
        c_layers = []
        for l in range(len(self.layers)):
            h_t, c_t = self.layers[l].get_states()
            h_layers.append(h_t.unsqueeze(Dim.batch))
            c_layers.append(c_t.unsqueeze(Dim.batch))

        h_layers = torch.cat(h_layers, dim=Dim.seq)
        c_layers = torch.cat(c_layers, dim=Dim.seq)
        return hidden_seq, (h_layers, c_layers)

