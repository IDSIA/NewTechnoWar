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

from core.agents import Agent, Parameters
from core.state import StateOfTheBoard
from learningParameters import TOTAL_STEPS

done = False
steps_done = 0  # counts total of actions while learning, over episodes and samples
roundOfPlay = 0  # counts number of steps in the game


# Building up a dummy scenario, called Scenario1
shape = (10, 10)
stateOfTheBoard = StateOfTheBoard(shape)
stateOfTheBoard.resetScenario1()


# setting up basic agent features
redParameters = Parameters('red', {})
blueParameters = Parameters('blue', {})

redAgent = Agent(roundOfPlay, redParameters)
blueAgent = Agent(roundOfPlay, blueParameters)


if __name__ == "__main__":

    # here goes the main loop
    while not done:

        # red agent chooses action
        redChosenFigure, redChosenAttackOrMove, redChosenAction, steps_done = redAgent.select_random_action(
            stateOfTheBoard, steps_done)
        # Update board, observe state and reward, to be implemented
        done = stateOfTheBoard.redStep(redChosenFigure.item(), redChosenAttackOrMove.item(), redChosenAction.item())

        # not sure if it makes sense but only the red agent updates step counter. Similarly, only win for blue is by time-out
        blueChosenFigure, blueChosenAttackOrMove, blueChosenAction, _ = blueAgent.select_random_action(
            stateOfTheBoard, steps_done)
        # Update board, observe state and reward, to be implemented
        __ = stateOfTheBoard.blueStep(blueChosenFigure.item(), blueChosenAttackOrMove.item(), blueChosenAction.item())

        if steps_done == TOTAL_STEPS:
            done = True
