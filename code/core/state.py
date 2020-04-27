import numpy as np

class StateOfTheBoard(object):

    """

    Just a description of the state of the game.

    """

    def __init__(self, shape: tuple):

        self.board = np.zeros(shape)

        self.obstacles = np.zeros(shape)

        self.geography = np.zeros(shape)

        self.figures = {

            'tanks': [],

            'infantries' : []

        }

    def addObstacle(self, pos:tuple, obstacle:int):

        self.obstacles[pos] = obstacle
