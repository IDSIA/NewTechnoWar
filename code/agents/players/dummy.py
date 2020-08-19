import numpy as np

from agents.players.player import Player
from core.actions import Action, Pass
from core.game.board import GameBoard
from core.game.manager import GameManager
from core.game.state import GameState

ACTION_MOVE = 0
ACTION_ATTACK = 1
ACTION_PASS = 2


class PlayerDummy(Player):

    def __init__(self, team: str):
        super().__init__('dummy', team)

    def __repr__(self):
        return f'{self.name}-{self.team}'

    def chooseAction(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        # choose which figures that can still be activate will be activated
        figures = state.getFiguresCanBeActivated(self.team)
        if not figures:
            raise ValueError(f"no more figures for {self.team}")

        f = np.random.choice(figures)

        moves = gm.buildMovements(board, state, f)
        attacks = gm.buildAttacks(board, state, f)

        if not moves and not attacks:
            raise ValueError(f"no more moves for {f} {self.team}")

        whatDo = [ACTION_PASS]

        if moves:
            whatDo.append(ACTION_MOVE)
        if attacks:
            whatDo.append(ACTION_ATTACK)

        # agent chooses type of action
        toa = np.random.choice(whatDo)

        actions = []

        if toa == ACTION_PASS:
            actions = [Pass(self.team, f)]

        if toa == ACTION_MOVE:
            actions = moves

        if toa == ACTION_ATTACK:
            actions = attacks

        return np.random.choice(actions)

    def chooseResponse(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        # choose to respond or not
        if not np.random.choice([True, False]):
            raise ValueError('no response given')

        # choose which figures that can still respond will respond
        figures = state.getFiguresCanRespond(self.team)
        if not figures:
            raise ValueError('no figure can respond')

        f = np.random.choice(figures)

        # build possible response for the chosen unit
        responses = gm.buildResponses(board, state, f)

        if responses:
            response = np.random.choice(responses)
            return response
        else:
            raise ValueError('no response available')
