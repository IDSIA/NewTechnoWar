from typing import Tuple

import torch.nn.functional as F
import torch.nn as nn
import torch


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

        self.conv1 = nn.Conv2d(board_levels, num_channels, 3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(num_channels, num_channels, 3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(num_channels, num_channels, 3, stride=1)
        self.conv4 = nn.Conv2d(num_channels, num_channels, 3, stride=1)

        self.bn1 = nn.BatchNorm2d(num_channels)
        self.bn2 = nn.BatchNorm2d(num_channels)
        self.bn3 = nn.BatchNorm2d(num_channels)
        self.bn4 = nn.BatchNorm2d(num_channels)

        self.fc1 = nn.Linear(num_channels*(self.board_x-4)*(self.board_y-4), 1024)
        self.fc_bn1 = nn.BatchNorm1d(1024)

        self.fc2 = nn.Linear(1024, 512)
        self.fc_bn2 = nn.BatchNorm1d(512)

        self.fc3 = nn.Linear(512, self.action_size)

        self.fc4 = nn.Linear(512, 1)

    def forward(self, s):
        #                                                           s: batch_size x board_x x board_y
        s = s.view(-1, self.board_levels, self.board_x, self.board_y)                # batch_size x 1 x board_x x board_y
        s = F.relu(self.bn1(self.conv1(s)))                          # batch_size x num_channels x board_x x board_y
        s = F.relu(self.bn2(self.conv2(s)))                          # batch_size x num_channels x board_x x board_y
        s = F.relu(self.bn3(self.conv3(s)))                          # batch_size x num_channels x (board_x-2) x (board_y-2)
        s = F.relu(self.bn4(self.conv4(s)))                          # batch_size x num_channels x (board_x-4) x (board_y-4)
        s = s.view(-1, self.num_channels * (self.board_x - 4) * (self.board_y - 4))

        s = F.dropout(F.relu(self.fc_bn1(self.fc1(s))), p=self.dropout, training=self.training)  # batch_size x 1024
        s = F.dropout(F.relu(self.fc_bn2(self.fc2(s))), p=self.dropout, training=self.training)  # batch_size x 512

        pi = self.fc3(s)                                                                         # batch_size x action_size
        v = self.fc4(s)                                                                          # batch_size x 1

        return F.log_softmax(pi, dim=1), torch.tanh(v)
