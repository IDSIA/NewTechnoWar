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

        # dynamic properties of the board
        self.redFigures = {
            'tanks': {},
            'infantries': {}
        }
        self.blueFigures = {
            'tanks': {},
            'infantries': {}
        }

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

    def addRedTank(self, tankId: int, tankPosition: tuple):
        tmp = np.np.zeros(self.shape, dtype='uint8')
        tmp[tankPosition] = 1
        self.redFigures['tanks'][tankId] = [tankPosition, tmp]

    def addRedInfantry(self, infantryId: int, infantryPosition: tuple):
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[infantryPosition] = 1
        self.redFigures['infantries'][infantryId] = [infantryPosition, tmp]

    def addBlueTank(self, tankId: int, tankPosition: tuple):
        tmp = np.np.zeros(self.shape, dtype='uint8')
        tmp[tankPosition] = 1
        self.blueFigures['tanks'][tankId] = [tankPosition, tmp]

    def addBlueInfantry(self, infantryId: int, infantryPosition: tuple):
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[infantryPosition] = 1
        self.blueFigures['infantries'][infantryId] = [infantryPosition, tmp]

    # sets up a specific scenario. reset to state of board to an initial state. Here this is just a dummy

    def resetScenario1(self):
        obstacles = np.zeros(self.shape, dtype='uint8')
        obstacles[(5, 5)] = 1
        self.addObstacle(obstacles)

        roads = np.zeros(self.shape, dtype='uint8')
        roads[0, :] = 1
        self.addRoads(roads)

        objective = np.zeros(self.shape, dtype='uint8')
        objective[9, 9] = 1
        self.addObjective(objective)

        self.addRedInfantry(infantryId=1, infantryPosition=(4, 1))
        self.addBlueInfantry(infantryId=1, infantryPosition=(5, 2))
    # applies action to the state of the board for both red and blue agents
    # the function is implemented twice, to be more easily called. also maybe there are different terminal conditions for red and blue. I am also

    def redStep(self, action):
        infantryId = 1  # this is just a dummy for now
        oldState = self.redFigures['infantries'][infantryId][0]
        newState = (self.redFigures['infantries'][infantryId][0][0] + self.actionMovesDict[action][0],
                    self.redFigures['infantries'][infantryId][0][1] + self.actionMovesDict[action][1])

        # if agent would jump off the board by some action it just remains at the hexagon
        if newState[0] < 0 or newState[0] >= self.shape[0]:
            newState = oldState
        if newState[1] < 0 or newState[1] >= self.shape[1]:
            newState = oldState

        # store things
        self.redFigures['infantries'][infantryId][0] = newState
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[newState] = 1
        self.redFigures['infantries'][infantryId][1] = tmp
        print(tmp)

        done = False  # dummy
        return done

    def blueStep(self, action):
        infantryId = 1  # this is just a dummy for now
        oldState = self.blueFigures['infantries'][infantryId][0]
        newState = (self.blueFigures['infantries'][infantryId][0][0] + self.actionMovesDict[action][0],
                    self.blueFigures['infantries'][infantryId][0][1] + self.actionMovesDict[action][1])

        # if agent would jump off the board by some action it just remains at the hexagon
        if newState[0] < 0 or newState[0] >= self.shape[0]:
            newState = oldState
        if newState[1] < 0 or newState[1] >= self.shape[1]:
            newState = oldState

        # store things
        self.blueFigures['infantries'][infantryId][0] = newState
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[newState] = 1
        self.blueFigures['infantries'][infantryId][1] = tmp

        done = False  # dummy
        return done
