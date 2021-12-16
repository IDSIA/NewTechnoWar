from typing import Tuple

import torch.nn.functional as F
import torch.nn as nn
import torch


class NTWModel(nn.Module):

    def __init__(self, shape: Tuple[int, int], lr: float = 0.001, dropout: float = 0.3, epochs: int = 2, batch_size: int = 64,
                 num_channels: int = 32, action_size: int = 1640, board_levels: int = 5):
        super(NTWModel, self).__init__()

        self.board_x, self.board_y = shape
        self.action_size: int = action_size

        self.lr: float = lr
        self.dropout: float = dropout

        self.epochs: int = epochs
        self.batch_size: int = batch_size
        self.num_channels: int = num_channels
        self.board_levels: int = board_levels

        # model definition
        self.layers_net = [
            # board_x * board_y * board_levels
            nn.Conv2d(board_levels, num_channels, kernel_size=2, stride=1, padding=0),
            nn.BatchNorm2d(num_channels),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=1, padding=1),
            # board_x-1 * board_y-1 * num_channels
            nn.Conv2d(num_channels, num_channels * 2, kernel_size=3, stride=1, padding=0),
            nn.BatchNorm2d(num_channels * 2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=1, padding=0),
            # board_x-2* board_y-2 * num_channels*2
            nn.Conv2d(num_channels * 2, num_channels * 4, kernel_size=3, stride=1, padding=0),
            nn.BatchNorm2d(num_channels * 4),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=1, padding=0),
            # board_x-3* board_y-3 * num_channels*4
            nn.Conv2d(num_channels * 4, num_channels * 8, kernel_size=3, stride=1, padding=0),
            nn.BatchNorm2d(num_channels * 8),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=1, padding=0),
            # board_x-4* board_y-4 * num_channels*8

            nn.Flatten(),

            # board_x-4 * board_y-4 * num_channels*8 + state_features
            nn.Linear((self.board_x-4) * (self.board_y-4) * board_levels, 2048),
            nn.BatchNorm1d(2048),
            nn.ReLU(),
            # 8192
            nn.Linear(2048, 2048),
            nn.BatchNorm1d(2048),
            nn.ReLU(),
            # 4096
            nn.Linear(2048, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            # 2048
        ]
        self.layers_out_pi = [
            nn.Linear(1024, action_size),
            # action_size
            nn.Softmax(dim=-1)
        ]
        self.layers_out_v = [
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, 1),
            # 1
            nn.Tanh()
        ]

        # model composition
        self.net = nn.Sequential(*self.layers_net)
        self.out_pi = nn.Sequential(*self.layers_out_pi)
        self.out_v = nn.Sequential(*self.layers_out_v)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x: batch_size * board_x * board_y * board_levels
        """
        x = x.view(-1, self.board_levels, self.board_x, self.board_y)
        x = self.net(x)

        pi = self.out_pi(x)
        v = self.out_v(x)

        return pi, v.reshape(-1)
