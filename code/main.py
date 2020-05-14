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
from core.agents import Agent, Parameters
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

redAgent = Agent(roundOfPlay, redParameters)
blueAgent = Agent(roundOfPlay, blueParameters)

if __name__ == "__main__":

    print(stateOfTheBoard)

    while not done:
        redChosenFigure, redChosenAttackOrMove, redChosenAction, steps_done = \
            redAgent.select_random_action(stateOfTheBoard, steps_done)

        done = stateOfTheBoard.step(RED, redChosenFigure.item(), redChosenAttackOrMove.item(), redChosenAction.item())

        print(stateOfTheBoard)

        blueChosenFigure, blueChosenAttackOrMove, blueChosenAction, _ = \
            blueAgent.select_random_action(stateOfTheBoard, steps_done)

        __ = stateOfTheBoard.step(BLUE, blueChosenFigure.item(), blueChosenAttackOrMove.item(), blueChosenAction.item())

        print(stateOfTheBoard)
        stateOfTheBoard.update()

        if steps_done == TOTAL_STEPS:
            done = True
