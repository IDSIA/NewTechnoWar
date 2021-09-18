from typing import Tuple

import torch.nn.functional as F
import torch.nn as nn
import torch
from torch.nn.modules.activation import ReLU


class NTWModel(nn.Module):

    def __init__(self, shape: Tuple[int, int], lr: float = 0.001, dropout: float = 0.3, epochs: int = 2, batch_size: int = 64,
                 num_channels: int = 512, action_size: int = 1640, board_levels: int = 3):
        super(NTWModel, self).__init__()

        self.board_x, self.board_y = shape
        self.action_size: int = action_size

        self.lr: float = lr
        self.dropout: float = dropout

        self.epochs: int = epochs
        self.batch_size: int = batch_size
        self.num_channels: int = num_channels
        self.board_levels: int = board_levels

        self.features_extraction = nn.Sequential(*[
            nn.Conv2d(board_levels, num_channels, 3, stride=1, padding=1),          # batch_size x num_channels x board_x x board_y
            nn.BatchNorm2d(num_channels),
            nn.ReLU(),
            nn.Conv2d(num_channels, num_channels, 3, stride=1, padding=1),          # batch_size x num_channels x board_x x board_y
            nn.BatchNorm2d(num_channels),
            nn.ReLU(),
            nn.Conv2d(num_channels, num_channels, 3, stride=1),                     # batch_size x num_channels x (board_x-2) x (board_y-2)
            nn.BatchNorm2d(num_channels),
            nn.ReLU(),
            nn.Conv2d(num_channels, num_channels, 3, stride=1),                     # batch_size x num_channels x (board_x-4) x (board_y-4)
            nn.BatchNorm2d(num_channels),
            nn.ReLU()
        ])
        self.fully_connected = nn.Sequential(*[
            nn.Linear(num_channels * (self.board_x-4) * (self.board_y-4), 2048),    # batch_size x 2048
            nn.BatchNorm1d(2048),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(2048, 1024),                                                  # batch_size x 2048
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Dropout(dropout),
        ])
        self.out_pi = nn.Sequential(*[
            nn.Linear(1024, action_size),                                           # batch_size x action_size
            nn.Softmax(dim=-1)
        ])
        self.out_v = nn.Sequential(*[
            nn.Linear(1024, 1),                                                     # batch_size x 1
            nn.Tanh()
        ])

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # x: batch_size x board_x x board_y x board_levels
        x = x.view(-1, self.board_levels, self.board_x, self.board_y)
        x = self.features_extraction(x)
        x = x.view(-1, self.num_channels * (self.board_x - 4) * (self.board_y - 4))
        x = self.fully_connected(x)

        pi = self.out_pi(x)
        v = self.out_v(x)

        return pi, v.view(len(x), 1)
