import os
import logging

from typing import Tuple
from tqdm import tqdm

import numpy as np
import torch
import torch.optim as optim

from torch.nn import L1Loss, MSELoss

from agents.reinforced.nn.NTWModel10x10 import NTWModel10x10
from core.game import MAX_UNITS_PER_TEAM

logger = logging.getLogger(__name__)


class ModelWrapper():

    def __init__(self, seed: int = 0, epochs: int = 2, batch_size: int = 64, device: str or None = 'cpu',
                 lr: float = 0.001, dropout: float = 0.3, board_levels: int = 6, state_features: int = 2829, max_units_per_team: int = MAX_UNITS_PER_TEAM
                 ):
        self.epochs: int = epochs
        self.batch_size: int = batch_size

        self.nn = NTWModel10x10(lr=lr, dropout=dropout, board_levels=board_levels, state_features=state_features, max_units_per_team=max_units_per_team)

        self.random = np.random.default_rng(seed)
        self.history = []

        self.device = device
        self.to(self.device)

    def to(self, device: str or None = None) -> None:
        self.device = device if device else 'cpu'
        self.nn = self.nn.to(self.device)

    def train(self, examples, team: str = None) -> None:
        """
        examples: list of examples, each example is of form (features, pi, v)
        """
        self.nn = self.nn.to(self.device)

        optimizer = optim.Adam(self.nn.parameters())
        n = len(examples)

        x_bd, x_st, y_pi, y_v = zip(*examples)
        x_bd = np.array(x_bd)
        x_st = np.array(x_st)
        y_pi = np.array(y_pi)
        y_v = np.array(y_v)

        team = team if team else ''

        batch_count = int(n / self.batch_size) + 1

        criterion_pi = L1Loss()
        criterion_v = MSELoss()

        t = tqdm(range(batch_count * self.epochs), desc=f'Training {team:4}')
        for epoch in range(self.epochs):
            self.nn.train()

            for batch in range(batch_count):
                sample_ids = self.random.choice(n, size=min(n, self.batch_size))

                f_bd = x_bd[sample_ids]
                f_st = x_st[sample_ids]
                pi = y_pi[sample_ids]
                v = y_v[sample_ids]

                f_bd = torch.FloatTensor(np.array(f_bd))
                f_st = torch.FloatTensor(np.array(f_st))
                target_pi = torch.FloatTensor(np.array(pi))
                target_v = torch.FloatTensor(np.array(v))

                # predict inputs
                f_bd = f_bd.contiguous().to(self.device)
                f_st = f_st.contiguous().to(self.device)
                target_pi = target_pi.contiguous().to(self.device)
                target_v = target_v.contiguous().to(self.device)

                # compute output
                out_pi, out_v = self.nn(f_bd, f_st)

                loss_pi = criterion_pi(out_pi, target_pi)
                loss_v = criterion_v(out_v, target_v)

                total_loss = loss_pi + loss_v

                # record loss
                t.set_postfix(Loss_pi=f'{loss_pi.item():.4}', Loss_v=f'{loss_v.item():.4}', Epoch=f'{epoch:3}', Batch=f'{batch:3}')
                t.update()

                # compute gradient and do SGD step
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()

                self.history.append((loss_pi.item(), loss_v.item(), len(sample_ids)))

        t.update()

    def predict(self, features_board: np.ndarray, features_state: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        # preparing input
        x_bd = torch.FloatTensor(features_board).to(self.device)
        x_st = torch.FloatTensor(features_state).to(self.device)

        self.nn = self.nn.to(self.device)
        self.nn.eval()

        with torch.no_grad():
            pi, v = self.nn(x_bd, x_st)

        return pi.data.cpu().numpy()[0], v.data.cpu().numpy()[0]

    # def loss_pi(self, targets, outputs):
    #     return -torch.sum(targets * outputs) / targets.size()[0]

    # def loss_v(self, targets, outputs):
    #     return torch.sum((targets - outputs.view(-1)) ** 2) / targets.size()[0]

    def save_checkpoint(self, folder: str = 'checkpoint', filename: str = 'checkpoint.pth.tar') -> None:
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            logger.info("Checkpoint Directory does not exist! Making directory %s", folder)
            os.mkdir(folder)

        torch.save({
            'state_dict': self.nn.state_dict(),
        }, filepath)

    def load_checkpoint(self, folder: str = 'checkpoint', filename: str = 'checkpoint.pth.tar') -> None:
        logger.debug('loading model from folder=%s file=%s', folder, filename)

        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise Exception("No model in path {}".format(filepath))
        map_location = torch.device('cpu') if self.device == 'cpu' else None
        checkpoint = torch.load(filepath, map_location=map_location)
        self.nn.load_state_dict(checkpoint['state_dict'])
