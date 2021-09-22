from typing import Tuple

import torch.nn.functional as F
import torch.nn as nn
import torch


class NTWModel10x10(nn.Module):

    def __init__(self, lr: float = 0.001, dropout: float = 0.3, num_channels: int = 32, action_size: int = 1640, board_levels: int = 6, state_features: int = 2828):
        super(NTWModel10x10, self).__init__()

        self.board_x, self.board_y = 10, 10
        self.action_size: int = action_size

        self.lr: float = lr
        self.dropout: float = dropout

        self.num_channels: int = num_channels
        self.board_levels: int = board_levels
        self.state_features: int = state_features

        # model definition
        self.layers_board = [
            nn.Flatten(),
        ]
        self.layers_net = [
            # board_x-4 * board_y-4 * num_channels*8 + state_features
            nn.Linear(self.board_x * self.board_y * board_levels + self.state_features, 2048),
            nn.BatchNorm1d(2048),
            nn.ReLU(),
            # 2048
            nn.Linear(2048, 2048),
            nn.BatchNorm1d(2048),
            nn.ReLU(),
            # 2048
            nn.Linear(2048, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            # 1024
        ]
        self.layers_out_pi = [
            nn.Linear(1024, action_size),
            # action_size
            nn.Softmax(dim=-1)
        ]
        self.layers_out_v = [
            # 1024
            nn.Linear(1024, 512),
            nn.ReLU(),
            # 512
            nn.Linear(512, 1),
            # 1
            nn.Tanh()
        ]

        # model composition
        self.net_board = nn.Sequential(*self.layers_board)
        self.net = nn.Sequential(*self.layers_net)
        self.out_pi = nn.Sequential(*self.layers_out_pi)
        self.out_v = nn.Sequential(*self.layers_out_v)

    def forward(self, x_b: torch.Tensor, x_s: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x_b: batch_size * board_x * board_y * board_levels
        x_s: batch_size * state_features
        """
        x_b = x_b.view(-1, self.board_levels, self.board_x, self.board_y)
        x_b = self.net_board(x_b)

        x = torch.cat((x_b, x_s), 1)

        x = self.net(x)

        pi = self.out_pi(x)
        v = self.out_v(x)

        return pi, v.reshape(-1)
