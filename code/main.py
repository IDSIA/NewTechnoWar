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
from core import TOTAL_TURNS, RED, BLUE

done = False
steps_done = 0  # counts total of actions while learning, over episodes and samples
roundOfPlay = 0  # counts number of steps in the game


# setting up basic agent features
redParameters = Parameters(RED, {})
blueParameters = Parameters(BLUE, {})

redAgent = Agent(roundOfPlay, redParameters)
blueAgent = Agent(roundOfPlay, blueParameters)

# Building up a dummy scenario, called Scenario1
shape = (10, 10)
stateOfTheBoard = StateOfTheBoard(shape)


def activation(first: Agent, second: Agent, turn: int):
    if stateOfTheBoard.canActivate(first):
        # red agent chooses action
        figure, action = first.select_random_action(stateOfTheBoard, turn)
        stateOfTheBoard.activate(action)

        # blue can choose to respond
        if stateOfTheBoard.canRespond(second):
            figureRespond, actionRespond = second.select_random_response(stateOfTheBoard, turn)
            stateOfTheBoard.activate(actionRespond)

        stateOfTheBoard.update()
        # TODO: print board?


def play():
    # this loop is a single game
    for turn in range(TOTAL_TURNS):

        while stateOfTheBoard.canActivate(redAgent) and stateOfTheBoard.canActivate(blueAgent):
            activation(redAgent, blueAgent, turn)
            activation(blueAgent, redAgent, turn)

        # observe state and reward, to be implemented
        redAgent.update(stateOfTheBoard, turn)
        blueAgent.update(stateOfTheBoard, turn)

        if stateOfTheBoard.goalAchieved():
            # TODO: implement rewards
            break

    return True


if __name__ == "__main__":

    # here goes the main loop
    while not done:

        # initialize game
        stateOfTheBoard.resetScenario1()

        done = play()

        if steps_done == TOTAL_STEPS:
            done = True
