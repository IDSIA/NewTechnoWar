import random
import numpy as np
from collections import namedtuple

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T



from core.state import StateOfTheBoard
from learningParameters import *

class Parameters(object):

    def __init__(self, team: str, params: dict):
        self.team = team
        self.params = params
        # here well probably put a neural net or similar.

class Agent(object):

    def __init__(self, stateOfTheBoard: StateOfTheBoard, roundOfPlay: int, parameters: Parameters):
        self.stateOfTheBoard = stateOfTheBoard
        self.roundOfPlay = roundOfPlay
        self.parameters = parameters

    #must implement an update method.

    #select eps greedy action with eps decay
    #def select_action(self, self.state, self.steps_done):
    #    sample = random.random()
    #   eps_threshold = EPS_END + (EPS_START - EPS_END) * \
    #   math.exp(-1. * steps_done / EPS_DECAY)
    #   steps_done += 1
    #if sample > eps_threshold:
       # with torch.no_grad():
           # return pNN(state).max(1)[1].view(1, 1), steps_done
    #else:
        #return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long), steps_done

    #select random action
    def select_random_action(self, stateOfTheBoard, steps_done):
        steps_done += 1
        return torch.tensor([[random.randrange(6)]], device=DEVICE, dtype=torch.long), steps_done
