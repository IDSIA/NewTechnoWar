import os
import logging

from typing import Tuple

import numpy as np

import torch
import torch.optim as optim
from tqdm import tqdm

from .NTWNNet import NTWNNet as ntwnet

logger = logging.getLogger(__name__)


class AverageMeter(object):
    """From https://github.com/pytorch/examples/blob/master/imagenet/main.py"""

    def __init__(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def __repr__(self):
        return f'{self.avg:.2e}'

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


class NNetWrapper():
    def __init__(self, shape: Tuple[int], seed: int = 0, lr: float = 0.001, dropout: float = 0.3, epochs: int = 2, batch_size: int = 64,
                 num_channels: int = 512, max_move_no_response_size: int = 1351, max_attack_size: int = 288
                 ):
        self.nnet = ntwnet(shape, lr, dropout, epochs, batch_size, num_channels, max_move_no_response_size, max_attack_size)
        self.board_x, self.board_y = shape  # TODO: replace with correct values ;;;;; game.getBoardSize()
        self.action_size = max_move_no_response_size + max_attack_size  # 5851 #game.getActionSize()

        self.epochs: int = epochs
        self.batch_size: int = batch_size

        self.random = np.random.default_rng(seed)
        self.history = []

        self.cuda: bool = torch.cuda.is_available()

        if self.cuda:
            self.nnet.cuda()

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        optimizer = optim.Adam(self.nnet.parameters())
        n = len(examples)

        for epoch in range(self.epochs):
            logger.info('EPOCH :: ' + str(epoch + 1))
            self.nnet.train()
            pi_losses = AverageMeter()
            v_losses = AverageMeter()

            batch_count = int(n / self.batch_size) + 1

            t = tqdm(range(batch_count), desc='Training Net')
            for _ in t:
                sample_ids = self.random.choice(n, size=min(n, self.batch_size))
                boards, pis, vs = list(zip(*[examples[i] for i in sample_ids]))
                boards = torch.FloatTensor(np.array(boards).astype(np.float64))
                target_pis = torch.FloatTensor(np.array(pis))
                target_vs = torch.FloatTensor(np.array(vs).astype(np.float64))

                # predict
                if self.cuda:
                    boards, target_pis, target_vs = boards.contiguous().cuda(), target_pis.contiguous().cuda(), target_vs.contiguous().cuda()

                # compute output
                out_pi, out_v = self.nnet(boards)
                l_pi = self.loss_pi(target_pis, out_pi)
                l_v = self.loss_v(target_vs, out_v)
                total_loss = l_pi + l_v

                # record loss
                pi_losses.update(l_pi.item(), boards.size(0))
                v_losses.update(l_v.item(), boards.size(0))
                t.set_postfix(Loss_pi=pi_losses, Loss_v=v_losses)

                # compute gradient and do SGD step
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()

                self.history.append(v_losses.avg)

    def predict(self, board):
        """
        board: np array with board
        """
        # preparing input
        board = torch.FloatTensor(board.astype(np.float64))

        if self.cuda:
            board = board.contiguous().cuda()
        board = board.view(1, self.board_x, self.board_y)
        self.nnet.eval()

        with torch.no_grad():
            pi, v = self.nnet(board)

        return torch.exp(pi).data.cpu().numpy()[0], v.data.cpu().numpy()[0]

    def loss_pi(self, targets, outputs):
        return -torch.sum(targets * outputs) / targets.size()[0]

    def loss_v(self, targets, outputs):
        return torch.sum((targets - outputs.view(-1)) ** 2) / targets.size()[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            logger.info("Checkpoint Directory does not exist! Making directory %s", folder)
            os.mkdir(folder)

        torch.save({
            'state_dict': self.nnet.state_dict(),
        }, filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise ("No model in path {}".format(filepath))
        map_location = None if self.cuda else 'cpu'
        checkpoint = torch.load(filepath, map_location=map_location)
        self.nnet.load_state_dict(checkpoint['state_dict'])
