import os
import pickle
import logging

import numpy as np

import torch

from agents.reinforced.nn.Wrapper import ModelWrapper

logger = logging.getLogger(__name__)


class Trainer:
    """
    This class is uesed for training the models with the new episodes.
    """

    model: ModelWrapper
    device: str
    team: str

    def __init__(self, model: ModelWrapper, team: str, device: str or None = None) -> None:
        self.model = model
        self.team = team

        if device:
            self.device = device
        else:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def train(self, train_examples: list, workdir: str, iteration: int):
        logger.info('using %s examples for training %s model', len(train_examples), self.team)

        # training new network
        self.model.to(self.device)
        self.model.train(train_examples, self.team)

        logger.info('Losses Average %s', self.model.history[-1])

        # save new model
        self.model.save_checkpoint(folder=os.path.join(workdir, 'models'), filename=f'checkpoint_model_{iteration}_{self.team}.pth.tar')
        self.model.save_checkpoint(folder=workdir, filename=f'model_{self.team}.pth.tar')

        # save metrics history
        filename = os.path.join(workdir, 'metrics', f'checkpoint_losses_{iteration}_{self.team}.tsv')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\t'.join(['i', 'l_pi_avg', 'l_pi_count', 'l_pi_sum', 'l_pi_val', 'l_v_avg', 'l_v_count', 'l_v_sum', 'l_v_val']))
            f.write('\n')
            for x in range(len(self.model.history)):
                l_pi, l_v = self.model.history[x]
                f.write('\t'.join([str(a) for a in [x, l_pi.avg, l_pi.count, l_pi.sum, l_pi.val, l_v.avg, l_v.count, l_v.sum, l_v.val]]))
                f.write('\n')
