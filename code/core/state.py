import numpy as np

from core import RED, BLUE, ACTION_MOVE, ACTION_ATTACK, TOTAL_TURNS
from utils.coordinates import hex_movement, Hex, hex_linedraw, to_hex


class StateOfTheBoard:
    """

    state of the board of the game

    """

    def __init__(self, shape: tuple):
        self.shape = shape
        self.turn = 0

        # this dictionary should contain ALL POSSIBLE moves,
        # so more moves have to be added here in appropriate representation
        self.actionMoves = hex_movement(Hex(0, 0), N=4)  # TODO: N is hardcoded, it should be based on figure type
        self.actionAttacks = {
            RED: [],
            BLUE: []
        }

        # static properties of the board
        self.board = {
            'obstacles': np.zeros(shape, dtype='uint8'),
            'terrain': np.zeros(shape, dtype='uint8'),
            'roads': np.zeros(shape, dtype='uint8'),
            'geography': np.zeros(shape, dtype='uint8'),
            'objective': np.zeros(shape, dtype='uint8')
        }

        # we use the following convention for access keys#
        # keys are integers that represent the figure,
        # eg {0 : ['tank',(0,1), matrixWith1At (0,1)]}, {1:['infantry',....]}, ...
        # this is to ensure that we can access figures by integer key, which encodes a figure selection action

        self.figures = {
            RED: [],
            BLUE: []
        }

    def isLegalMove(self, oldFigurePosition, newFigurePosition):
        # check if position is still in the board
        conditions1 = 0 <= newFigurePosition[0] < self.shape[0]
        conditions2 = 0 <= newFigurePosition[1] < self.shape[1]

        if not (conditions1 and conditions2):
            return False

        # check for los on destination
        los = hex_linedraw(to_hex(oldFigurePosition), to_hex(newFigurePosition))
        for h in los:
            if self.board['obstacles'][h] > 0:
                print(f"{newFigurePosition} hidden from {oldFigurePosition} ")
                return False

        # check if position is an obstacle
        c1 = self.board['obstacles'][newFigurePosition] > 0

        # check if position is occupied by a figure
        c2 = any([newFigurePosition == f[1] for f in self.figures[RED]])
        c3 = any([newFigurePosition == f[1] for f in self.figures[BLUE]])

        return not (c1 or c2 or c3)

    def isLegalAttack(self, attackerPosition, targetPosition):
        if attackerPosition == targetPosition:
            return False

        los = hex_linedraw(to_hex(attackerPosition), to_hex(targetPosition))

        for h in los:
            if self.board['obstacles'][h] > 0:
                return False

        return True

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

    def addFigure(self, team: str, figureType: str, position: tuple):
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[position] = 1
        if team == RED:
            self.actionAttacks[BLUE].append(len(self.figures[RED]))
            self.figures[RED].append([figureType, position, tmp, True])  # here we add more attributes
        else:
            self.actionAttacks[RED].append(len(self.figures[BLUE]))
            self.figures[BLUE].append([figureType, position, tmp, True])  # here we add more attributes

    # sets up a specific scenario. reset to state of board to an initial state. Here this is just a dummy
    def resetScenario1(self):
        obstacles = np.zeros(self.shape, dtype='uint8')
        obstacles[(4, 5)] = 1
        obstacles[(5, 5)] = 1
        obstacles[(5, 4)] = 1
        self.addObstacle(obstacles)

        roads = np.zeros(self.shape, dtype='uint8')
        roads[0, :] = 1
        self.addRoads(roads)

        objective = np.zeros(self.shape, dtype='uint8')
        objective[9, 9] = 1
        self.addObjective(objective)

        self.addFigure(RED, 'infantry', (4, 1))
        self.addFigure(RED, 'tank', (4, 3))
        self.addFigure(BLUE, 'infantry', (5, 2))

    # applies action to the state of the board for both red and blue agents
    # the function is implemented twice, to be more easily called.
    # also maybe there are different terminal conditions for red and blue. I am also

    def step(self, team, chosenFigure, chosenAttackOrMove, chosenAction):
        otherTeam = RED if team is BLUE else RED
        figure = self.figures[team][chosenFigure]

        # move the chosen figure, chosenAttackOrMove isnt implemented yet, does have no effect at the momment
        if chosenAttackOrMove == ACTION_MOVE:
            oldFigurePosition = figure[1]
            newFigurePosition = (oldFigurePosition[0] + self.actionMoves[chosenAction][0],
                                 oldFigurePosition[1] + self.actionMoves[chosenAction][1])

            if self.isLegalMove(oldFigurePosition, newFigurePosition):
                # store things
                figure[1] = newFigurePosition
                figure[2][oldFigurePosition] = 0
                figure[2][newFigurePosition] = 1
                print(f"move from {oldFigurePosition} to {newFigurePosition}")
            else:
                print(f"invalid move from {oldFigurePosition} to {newFigurePosition}")

        if chosenAttackOrMove == ACTION_ATTACK:
            attackerPosition = figure[1]
            targetPosition = self.figures[otherTeam][self.actionAttacks[team][chosenAction]][1]

            if self.isLegalAttack(attackerPosition, targetPosition):
                print(f"{attackerPosition} shoot at {targetPosition}")
            else:
                print(f"invalid {attackerPosition} shoot at {targetPosition}")

        done = False  # dummy
        return done

    def __repr__(self):
        board = np.zeros(self.shape, dtype="uint8")

        for f in self.figures[RED]:
            board += f[2]
        for f in self.figures[BLUE]:
            board += f[2] * 2

        board += self.board['obstacles'] * 8
        board += self.board['objective'] * 5

        return str(board).replace("0", ".").replace("8", "X").replace("5", "G")

    def update(self):
        self.turn += 1

        for agent in [RED, BLUE]:
            for figure in self.figures[agent]:
                figure[3] = True

    def whoWon(self):
        objectives = self.board['objectives']

        for figure in self.figures[RED]:
            if objectives[figure[1]] > 0:
                return RED

        if self.turn >= TOTAL_TURNS:
            return BLUE

        return None

    def hashValue(self) -> int:
        """Encode the current state of the game (board positions) as an integer."""

        # positive numbers are RED figures, negatives are BLUE figures
        m = np.zeros(self.shape, dtype='uint8')
        for agent in [RED, BLUE]:
            c = 1 if agent is RED else 2
            for figure in self.figures[agent]:
                m += figure[2] * c

        return hash(str(m))
