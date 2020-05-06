import numpy as np

from core.figures import Figure, Infantry, Tank, TYPE_VEHICLE, TYPE_INFANTRY
from core.actions import Action, Move, Shoot, Respond
from utils.coordinates import Hex, hex_reachable
from utils.colors import red, redBg, blue, blueBg, yellow, pinkBg, grayBg


class StateOfTheBoard:
    """

    state of the board of the game

    """

    def __init__(self, shape: tuple, teamRed: str, teamBlue: str):
        self.shape = shape

        self.red = teamRed
        self.blue = teamBlue

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
            'objective': np.zeros(shape, dtype='uint8'),
            'figures': {
                self.red: np.zeros(shape, dtype='uint8'),
                self.blue: np.zeros(shape, dtype='uint8'),
            }
        }

        self.nextRedFigureId = 0
        self.nextBlueFigureId = 0
        # dynamic properties of the board

        # access to figures is done by index: [agent][figure]. Each figure know its own state
        self.figures = {
            self.red: [],
            self.blue: []
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

    def addFigure(self, agent: str, figure: Figure):
        figures = self.figures[agent]

        figures.append(figure)
        index = len(figures)
        figure.index = index
        self.board['figures'][agent][figure.position] = index

    def getFigureByPos(self, agent: str, pos: tuple):
        index = self.board['figures'][agent][pos]
        return self.figures[agent][index - 1]

    def resetScenario1(self):
        """
        Sets up a specific scenario. reset to state of board to an initial state.
        Here this is just a dummy.
        """
        # TODO: make StateOfTheBoard abstract, with "reset" method abstract and implement it in a new class

        obstacles = np.zeros(self.shape, dtype='uint8')
        obstacles[(4, 4)] = 1
        self.addObstacle(obstacles)

        roads = np.zeros(self.shape, dtype='uint8')
        roads[0, :] = 1
        self.addRoads(roads)

        objective = np.zeros(self.shape, dtype='uint8')
        objective[4, 5] = 1
        self.addObjective(objective)

        self.addFigure(self.red, Infantry(position=(1, 1), name='rInf1'))
        self.addFigure(self.red, Tank(position=(1, 2), name='rTank1'))
        self.addFigure(self.blue, Infantry(position=(3, 3), name='bInf1'))

    # applies action to the state of the board for both red and blue agents
    # the function is implemented twice, to be more easily called. also maybe there are different terminal conditions for red and blue. I am also

    def redStep(self, chosenFigure, chosenAttackOrMove, chosenAction):

        redFigures = self.figures[self.red]

        # move the chosen figure, chosenAttackOrMove isnt implemented yet, does have no effect at the momment
        oldState = redFigures[chosenFigure][1]
        newState = (redFigures[chosenFigure][1][0] + self.actionMovesDict[chosenAction][0],
                    redFigures[chosenFigure][1][1] + self.actionMovesDict[chosenAction][1])

        # if agent would jump off the board by some action it just remains at the hexagon
        if newState[0] < 0 or newState[0] >= self.shape[0]:
            newState = oldState
        if newState[1] < 0 or newState[1] >= self.shape[1]:
            newState = oldState

        # store things
        redFigures[chosenFigure][1] = newState
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[newState] = 1
        redFigures[chosenFigure][2] = tmp
        print(chosenFigure)
        print(tmp)

        done = False  # dummy
        return done

    def blueStep(self, chosenFigure, chosenAttackOrMove, chosenAction):

        blueFigures = self.figures[self.blue]

        # move the chosen figure, chosenAttackOrMove isnt implemented yet, does have no effect at the momment
        oldState = blueFigures[chosenFigure][1]
        newState = (blueFigures[chosenFigure][1][0] + self.actionMovesDict[chosenAction][0],
                    blueFigures[chosenFigure][1][1] + self.actionMovesDict[chosenAction][1])

        # if agent would jump off the board by some action it just remains at the hexagon
        if newState[0] < 0 or newState[0] >= self.shape[0]:
            newState = oldState
        if newState[1] < 0 or newState[1] >= self.shape[1]:
            newState = oldState

        # store things
        blueFigures[chosenFigure][1] = newState
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[newState] = 1
        blueFigures[chosenFigure][2] = tmp

        done = False  # dummy
        return done

    def activableFigures(self, team: str):
        return [f for f in self.figures[team] if not f.activated]

    def canActivate(self, team: str):
        return len(self.activableFigures(team)) > 0

    def buildActions(self, team: str):
        actions = []

        for figure in self.figures[team]:

            pos = Hex(figure.pos, figure.col)
            distance = figure.move - figure.load
            if (figure.kind == TYPE_INFANTRY):
                distance += 1
            elif (figure.kind == TYPE_VEHICLE):
                distance += 2

            # TODO: add obstacles
            movements = hex_reachable(pos, distance, set())

            for movement in movements:
                actions.append(Move(figure, movement))

        return actions

    def activate(self, action: Action):
        # TODO: perform action with figure
        pass

    def canRespond(self, team: str):
        # TODO:
        return False

    def goalAchieved(self):
        # TODO:
        return False

    def print(self, size=3):
        cols, rows = self.shape

        sep_horizontal = '+'.join(['-' * size] * cols)

        print('+', sep_horizontal, '+')
        for i in range(rows):
            line = []
            for j in range(cols):
                cell = [' '] * size

                if self.board['objective'][i, j] > 0:
                    cell[1] = yellow('x')

                redFigure = self.board['figures']['red'][i, j]
                if redFigure > 0:
                    figure = self.getFigureByPos('red', (i, j))

                    cell[1] = red('T') if figure.kind == TYPE_VEHICLE else red('I')

                blueFigure = self.board['figures']['blue'][i, j]
                if blueFigure > 0:
                    figure = self.getFigureByPos('blue', (i, j))

                    cell[1] = blue('T') if figure.kind == TYPE_VEHICLE else blue('I')

                cell = ''.join(cell)

                if self.board['obstacles'][i, j] > 0:
                    cell = pinkBg(cell)
                if self.board['roads'][i, j] > 0:
                    cell = grayBg(cell)

                line.append(cell)

            mid = '|'.join([l for l in line])

            print('|', mid, '|')
        print('+', sep_horizontal, '+')
