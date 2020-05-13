import numpy as np


class StateOfTheBoard:
    """

    state of the board of the game

    """

    def __init__(self, shape: tuple):
        self.shape = shape
        
        #this dictionary should contain ALL POSSIBLE moves, so more moves have to be added here in appropriate representation
        self.actionMovesDict = {
            0: [0, 0],
            1: [-1, 0],
            2: [-1, -1],
            3: [0, -1],
            4: [1, 1],
            5: [1, 0],
            6: [1, 0]}
        

        # static properties of the board
        self.board = {
            'obstacles': np.zeros(shape, dtype='uint8'),
            'terrain': np.zeros(shape, dtype='uint8'),
            'roads': np.zeros(shape, dtype='uint8'),
            'geography': np.zeros(shape, dtype='uint8'),
            'objective': np.zeros(shape, dtype='uint8')
        }


        # we use the following convention for access keys#
        # keys are integers that represent the figure, eg {0 : ['tank',(0,1), matrixWith1At (0,1)]}, {1:['infantry',....]}, ...
        # this is to ensure that we can access figures by integer key, which encodes a figure selection action
        
        self.redFigures = []
        self.blueFigures = []

    def isLegalAction(self, newFigurePosition):
        #check if position is still in the board
        condition1 =  not (newFigurePosition[0] < 0 or newFigurePosition[0] >= self.shape[0])
        condition2 = not (newFigurePosition[1] < 0 or newFigurePosition[1] >= self.shape[1])
        return condition1 and condition2
        
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

    def addFigure(self, team : str, figureType : str, position: tuple):
        tmp = np.zeros(self.shape, dtype='uint8')
        tmp[position] = 1
        if(team=='blue'):
            self.redFigures.append([figureType, position, tmp])#here we add more attributes
        elif(team=='red'):
            self.blueFigures.append([figureType, position, tmp])#here we add more attributes
        else:
            print('error')


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

        self.addFigure( team='red', figureType='infantry', position=(4, 1))
        self.addFigure( team='red', figureType='tank', position=(4, 3))
        self.addFigure( team='blue', figureType='infantry', position=(5, 2))
    # applies action to the state of the board for both red and blue agents
    # the function is implemented twice, to be more easily called. also maybe there are different terminal conditions for red and blue. I am also

    def redStep(self, chosenFigure, chosenAttackOrMove, chosenAction):
        
        #move the chosen figure, chosenAttackOrMove isnt implemented yet, does have no effect at the momment
        oldFigurePosition = self.redFigures[chosenFigure][1]
        newFigurePosition = (oldFigurePosition[0] + self.actionMovesDict[chosenAction][0],
                    oldFigurePosition[1] + self.actionMovesDict[chosenAction][1])
        if(self.isLegalAction(newFigurePosition)):
            # store things
            self.redFigures[chosenFigure][1] = newFigurePosition
            self.redFigures[chosenFigure][2][oldFigurePosition] = 0
            self.redFigures[chosenFigure][2][newFigurePosition] = 1
            print(self.redFigures[chosenFigure][2])

        done = False  # dummy
        return done

    def blueStep(self, chosenFigure, chosenAttackOrMove, chosenAction):

        #move the chosen figure, chosenAttackOrMove isnt implemented yet, does have no effect at the momment
        oldFigurePosition = self.blueFigures[chosenFigure][1]
        newFigurePosition = (oldFigurePosition[0] + self.actionMovesDict[chosenAction][0],
                    oldFigurePosition[1] + self.actionMovesDict[chosenAction][1])
        if(self.isLegalAction(newFigurePosition)):
            # store things
            self.blueFigures[chosenFigure][1] = newFigurePosition
            self.blueFigures[chosenFigure][2][oldFigurePosition] = 0
            self.blueFigures[chosenFigure][2][newFigurePosition] = 1
            print(self.blueFigures[chosenFigure][2])

        done = False  # dummy
        return done
