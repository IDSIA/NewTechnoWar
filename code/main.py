"""
Main program.
"""
import math
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

from core import RED, BLUE
from core.agents import RandomAgent, MinMaxAgent, AlphaBetaAgent,  Parameters
from core.state import StateOfTheBoard
from learningParameters import TOTAL_STEPS

done = False
steps_done = 0
roundOfPlay = 0

shape = (10, 10)
stateOfTheBoard = StateOfTheBoard(shape)
stateOfTheBoard.resetScenario1()

redParameters = Parameters('red', {})
blueParameters = Parameters('blue', {})

redAgent = AlphaBetaAgent(roundOfPlay, redParameters)
blueAgent = RandomAgent(roundOfPlay, blueParameters)

if __name__ == "__main__":

    print(stateOfTheBoard)

    while not done:
        redChosenFigure, redChosenAttackOrMove, redChosenAction, steps_done = \
            redAgent.selectAction(stateOfTheBoard, steps_done)
            
        _ = stateOfTheBoard.step(RED, redChosenFigure, redChosenAttackOrMove, redChosenAction)
        print('red action')
        print(redChosenFigure)
        print(redChosenAction)
        print(_)
        print('board after red action:')
        print(stateOfTheBoard)
        blueChosenFigure, blueChosenAttackOrMove, blueChosenAction, _ = \
            blueAgent.selectAction(stateOfTheBoard, steps_done)
        __ = stateOfTheBoard.step(BLUE, blueChosenFigure.item(), 1, blueChosenAction.item())
        print('board after blue action:')
        print(stateOfTheBoard)
        stateOfTheBoard.update()
        done = stateOfTheBoard.whoWon()
        if steps_done == TOTAL_STEPS:
                done = True
