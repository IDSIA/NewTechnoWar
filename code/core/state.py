import numpy as np


class StateOfTheBoard:
    """

    state of the board of the game

    """

    def __init__(self, shape: tuple):
        self.shape = shape
        self.actionMovesDict = {
            0: [0, 0],
            1: [-1, 0],
            2: [-1, -1],
            3: [0, -1],
            4: [1, 1],
            5: [1, 0],
            6: [1, 0]
        }

        # static properties of the board
        self.board = {
            'obstacles': np.zeros(shape, dtype='uint8'),
            'terrain': np.zeros(shape, dtype='uint8'),
            'roads': np.zeros(shape, dtype='uint8'),
            'geography': np.zeros(shape, dtype='uint8'),
            'objective': np.zeros(shape, dtype='uint8')
        }

        self.nextRedFigureId = 0
        self.nextBlueFigureId = 0
        # dynamic properties of the board

        # we use the following convention for access keys#
        # keys are integers that represent the figure, eg {0 : ['tank',(0,1), matrixWith1At (0,1)]}, {1:['infantry',....]}, ...
        # this is to ensure that we can access figures by integer key, which encodes a figure selection action
        self.redFigures = {}
        self.blueFigures = {}

    def addObstacle(self, obstacles: np.array):
        self.board['obstacles'] = obstacles

    def addTerrain(self, terrain: np.array):
        self.board['terrain'] = terrain

    def addRoads(self, roads: np.array):
        self.board['roads'] = roads

    def addGeography(self, geography: np.array):
        self.board['geography'] = geography

    def addObjective(self, objective: np.array):
        self.board['objective'] = objective

    def addRedFigure(self, type: str, position: tuple):
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[position] = 1
        self.redFigures[self.nextRedFigureId] = [type, position, tmp]
        self.nextRedFigureId += 1

    def addBlueFigure(self, type: str, position: tuple):
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[position] = 1
        self.blueFigures[self.nextBlueFigureId] = [type, position, tmp]
        self.nextBlueFigureId += 1

    def resetScenario1(self):
        """
        Sets up a specific scenario. reset to state of board to an initial state.
        Here this is just a dummy.
        """
        # TODO: make StateOfTheBoard abstract, with "reset" method abstract and implement an update method

        obstacles = np.zeros(self.shape, dtype='uint8')
        obstacles[(5, 5)] = 1
        self.addObstacle(obstacles)

        roads = np.zeros(self.shape, dtype='uint8')
        roads[0, :] = 1
        self.addRoads(roads)

        objective = np.zeros(self.shape, dtype='uint8')
        objective[9, 9] = 1
        self.addObjective(objective)

        self.addRedFigure(type='infantry', position=(4, 1))
        self.addRedFigure(type='tank', position=(4, 3))
        self.addBlueFigure(type='infantry', position=(5, 2))

    # applies action to the state of the board for both red and blue agents
    # the function is implemented twice, to be more easily called. also maybe there are different terminal conditions for red and blue. I am also

    def redStep(self, chosenFigure, chosenAttackOrMove, chosenAction):

        # move the chosen figure, chosenAttackOrMove isnt implemented yet, does have no effect at the momment
        oldState = self.redFigures[chosenFigure][1]
        newState = (self.redFigures[chosenFigure][1][0] + self.actionMovesDict[chosenAction][0],
                    self.redFigures[chosenFigure][1][1] + self.actionMovesDict[chosenAction][1])

        # if agent would jump off the board by some action it just remains at the hexagon
        if newState[0] < 0 or newState[0] >= self.shape[0]:
            newState = oldState
        if newState[1] < 0 or newState[1] >= self.shape[1]:
            newState = oldState

        # store things
        self.redFigures[chosenFigure][1] = newState
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[newState] = 1
        self.redFigures[chosenFigure][2] = tmp
        print(chosenFigure)
        print(tmp)

        done = False  # dummy
        return done

    def blueStep(self, chosenFigure, chosenAttackOrMove, chosenAction):

        # move the chosen figure, chosenAttackOrMove isnt implemented yet, does have no effect at the momment
        oldState = self.redFigures[chosenFigure][1]
        newState = (self.redFigures[chosenFigure][1][0] + self.actionMovesDict[chosenAction][0],
                    self.redFigures[chosenFigure][1][1] + self.actionMovesDict[chosenAction][1])

        # if agent would jump off the board by some action it just remains at the hexagon
        if newState[0] < 0 or newState[0] >= self.shape[0]:
            newState = oldState
        if newState[1] < 0 or newState[1] >= self.shape[1]:
            newState = oldState

        # store things
        self.blueFigures[chosenFigure][1] = newState
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[newState] = 1
        self.blueFigures[chosenFigure][2] = tmp

        done = False  # dummy
        return done
