import random
import numpy as np
from collections import namedtuple

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

from core.state import StateOfTheBoard
from learningParameters import DEVICE


class Parameters:

    def __init__(self, team: str, params: dict):
        self.team = team
        self.params = params
        # here well probably put a neural net or similar.


class Agent:

    def __init__(self, roundOfPlay: int, parameters: Parameters):
        self.roundOfPlay = roundOfPlay
        self.parameters = parameters
        self.team = parameters.team

    # must implement an update method.

    # select eps greedy action with eps decay
    # def select_action(self, self.state, self.steps_done):
    #    sample = random.random()
    #   eps_threshold = EPS_END + (EPS_START - EPS_END) * \
    #   math.exp(-1. * steps_done / EPS_DECAY)
    #   steps_done += 1
    # if sample > eps_threshold:
    #     with torch.no_grad():
    #         return pNN(state).max(1)[1].view(1, 1), steps_done
    # else:
    #     return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long), steps_done

    # select random action
    # steps_done is NOT a member for performance
    def select_random_action(self, stateOfTheBoard, steps_done):
        # structure of action choice should be probably as follows:
        # 1) choose a figure.
        # 2) choose if to attack or move
        # 2a) if attack: choose whom to attack, according to game rules like line of sight and similar
        # 2b) if move: choose where to move, according to game rulse like roads and board boundaries

        # at the moment all this is implemented in terms of fully random actions, in a dummy code
        # in the real setup this is going to be too inefficient probably. will have to think of different representation
        if(self.team == 'red'):
            figures = stateOfTheBoard.redFigures
        elif(self.team == 'blue'):
            figures = stateOfTheBoard.blueFigures
        else:
            print(DEVICE + ' vote for socialicm!')
        chosenFigure = torch.tensor([[random.randrange(max(figures.keys())+1)]], device=DEVICE, dtype=torch.long)
        #chosenAttackOrMove = torch.tensor([[random.randrange(2)]], device=DEVICE, dtype=torch.long)
        chosenAction = torch.tensor([[random.randrange(6)]], device=DEVICE, dtype=torch.long)
        #steps_done += 1
        #
        return chosenFigure, chosenAction

    def select_random_response(self, stateOfTheBoard, turn):
        # TODO
        return None, None

    def update(self, stateOfTheBoard, turn):
        # TODO
        pass
