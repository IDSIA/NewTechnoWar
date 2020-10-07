from agents import Agent
from core import GM
from core.actions import Action
from core.game.board import GameBoard
from core.game.state import GameState


class SimpleMLAgent(Agent):

    def __init__(self, team: str, params: dict):
        super().__init__('SimpleML', team)

        self.params: dict = params
        self.model = params['model']  # has .predict(X) -> np.array

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        scores = []

        for figure in state.getFiguresCanBeActivated(self.team):
            actions = [GM.actionPassFigure(figure)] + \
                      GM.buildAttacks(board, state, figure) + \
                      GM.buildMovements(board, state, figure)

            for action in actions:
                newState, outcome = GM.activate(board, state, action)

                # apply classification pipeline
                X = newState.vector()
                score = self.model.predict(X)

                scores.append((score, action))

        # find better action
        bestScore, bestAction = 0.0, None

        for score, action in scores:
            if score > bestScore:
                bestScore, bestAction = score, action

        return bestAction

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        # TODO: get inspiration from GreedyAgent.chooseResponse()
        return super().chooseResponse(board, state)

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        # TODO: copy from other agents or find a better idea?
        super().placeFigures(board, state)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        # TODO: copy from other agents or find a better idea?
        super().chooseFigureGroups(board, state)
