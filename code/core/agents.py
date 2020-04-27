from core.state import StateOfTheBoard

class Parameters(object):

    def __init__(self, team: str, params: dict):
        self.team = team
        self.params = params


class Agent(object):

    def __init__(self, stateOfTheBoard: StateOfTheBoard, roundOfPlay: int, parameters: Parameters):

        self.stateOfTheBoard = stateOfTheBoard
        self.roundOfPlay = roundOfPlay
        self.parameters = parameters


    def actions(self):
        """
        Tell possible actions.
        """

        pass

    def takeAction(self):
        """
        Take an action.
        """

        return 0