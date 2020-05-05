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
from core import TOTAL_TURNS

done = False
steps_done = 0  # counts total of actions while learning, over episodes and samples
roundOfPlay = 0  # counts number of steps in the game


# Building up a dummy scenario, called Scenario1
shape = (10, 10)
stateOfTheBoard = StateOfTheBoard(shape)


# setting up basic agent features
redParameters = Parameters('red', {})
blueParameters = Parameters('blue', {})

redAgent = Agent(roundOfPlay, redParameters)
blueAgent = Agent(roundOfPlay, blueParameters)


if __name__ == "__main__":

    # here goes the main loop
    while not done:

        # initialize game
        stateOfTheBoard.resetScenario1()

        # this loop is a single game
        for turn in range(TOTAL_TURNS):

            while stateOfTheBoard.red_inactive_figures() > 0 and stateOfTheBoard.blue_inactive_figures() > 0:
                if stateOfTheBoard.red_inactive_figures() > 0:
                    # red agent chooses action
                    redFigure, redAction = redAgent.select_random_action(stateOfTheBoard, turn)
                    stateOfTheBoard.red_activate(redFigure, redAction)

                    # blue can choose to respond
                    if stateOfTheBoard.blue_can_respond():
                        blueFigureRespond, blueActionRespond = blueAgent.select_random_response(stateOfTheBoard, turn)
                        stateOfTheBoard.blue_activate(blueFigureRespond, blueActionRespond)

                if stateOfTheBoard.blue_inactive_figures() > 0:
                    # blue agent chooses action
                    blueFigure, blueAction = blueAgent.select_random_action(stateOfTheBoard, turn)

                    # red can chose to respon:
                    if stateOfTheBoard.red_can_respond():
                        redFigureRespond, redActionRespond = redAgent.select_random_response(stateOfTheBoard, turn)
                        stateOfTheBoard.red_activate(redFigureRespond, redActionRespond)

            # observe state and reward, to be implemented
            redAgent.update(stateOfTheBoard, turn)
            blueAgent.update(stateOfTheBoard, turn)

            if stateOfTheBoard.goal_achieved():
                # TODO: implement rewards
                done = True
                break

        if steps_done == TOTAL_STEPS:
            done = True
