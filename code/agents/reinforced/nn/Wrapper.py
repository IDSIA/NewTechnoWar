import os
import logging

from typing import Tuple
from tqdm import tqdm

import numpy as np
import torch
import torch.optim as optim

from agents.reinforced.nn.NTWModel import NTWModel

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


class ModelWrapper():

    def __init__(self, shape: Tuple[int], seed: int = 0, epochs: int = 2, batch_size: int = 64, num_channels: int = 512,
                 max_move_no_response_size: int = 1351, max_attack_size: int = 288, device='cpu',
                 lr: float = 0.001, dropout: float = 0.3,
                 ):
        self.board_x, self.board_y = shape
        self.action_size = max_move_no_response_size + max_attack_size + 1

        self.nn = NTWModel(shape, lr, dropout, epochs, batch_size, num_channels, self.action_size)

        self.epochs: int = epochs
        self.batch_size: int = batch_size

        self.random = np.random.default_rng(seed)
        self.history = []

        self.device = device
        self.to(self.device)

    def to(self, device=None):
        self.device = device if device else 'cpu'
        self.nn = self.nn.to(self.device)

    def train(self, examples, team=None):
        """
        examples: list of examples, each example is of form (features, pi, v)
        """
        self.nn = self.nn.to(self.device)

        optimizer = optim.Adam(self.nn.parameters())
        n = len(examples)

        team = team if team else ''

        batch_count = int(n / self.batch_size) + 1

        t = tqdm(range(batch_count * self.epochs), desc=f'Training {team:4}')
        for epoch in range(self.epochs):
            self.nn.train()
            pi_losses = AverageMeter()
            v_losses = AverageMeter()

            for batch in range(batch_count):
                sample_ids = self.random.choice(n, size=min(n, self.batch_size))
                features, pis, vs = list(zip(*[examples[i] for i in sample_ids]))
                features = torch.FloatTensor(np.array(features).astype(np.float64))
                target_pis = torch.FloatTensor(np.array(pis))
                target_vs = torch.FloatTensor(np.array(vs).astype(np.float64))

                # predict inputs
                features = features.contiguous().to(self.device)
                target_pis = target_pis.contiguous().to(self.device)
                target_vs = target_vs.contiguous().to(self.device)

                # compute output
                out_pi, out_v = self.nn(features)
                l_pi = self.loss_pi(target_pis, out_pi)
                l_v = self.loss_v(target_vs, out_v)
                total_loss = l_pi + l_v

                # record loss
                pi_losses.update(l_pi.item(), features.size(0))
                v_losses.update(l_v.item(), features.size(0))

                t.set_postfix(Loss_pi=pi_losses, Loss_v=v_losses, Epoch=epoch, Batch=batch)
                t.update()

                # compute gradient and do SGD step
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()

                self.history.append((pi_losses, v_losses))

    def predict(self, features):
        """
        board: np array with board
        """
        # preparing input
        data = torch.FloatTensor(features.astype(np.float64)).contiguous().to(self.device)

        data = data.view(3, self.board_x, self.board_y)
        self.nn = self.nn.to(self.device)
        self.nn.eval()

        with torch.no_grad():
            pi, v = self.nn(data)

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
            'state_dict': self.nn.state_dict(),
        }, filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        logger.debug('loading model from folder=%s file=%s', folder, filename)

        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise Exception("No model in path {}".format(filepath))
        map_location = torch.device('cpu') if self.device == 'cpu' else None
        checkpoint = torch.load(filepath, map_location=map_location)
        self.nn.load_state_dict(checkpoint['state_dict'])
