import numpy as np

from core.actions import Action, ACTION_MOVE, ACTION_ATTACK, ACTION_PASS, Pass
from core.game.board import GameBoard
from core.game.manager import GameManager
from core.game.state import GameState
from web.server.players.player import Player


class PlayerDummy(Player):

    def __init__(self, team: str):
        super().__init__('dummy', team)

    def __repr__(self):
        return f'{self.name}-{self.team}'

    def chooseAction(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        # choose which figures that can still be activate will be activated
        figures = state.getFiguresActivatable(self.team)
        if not figures:
            raise ValueError(f"no more figures for {self.team}")

        f = np.random.choice(figures)

        moves = gm.buildMovements(board, state, self.team, f)
        shoots = gm.buildShoots(board, state, self.team, f)

        if not moves and not shoots:
            raise ValueError(f"no more moves for {f} {self.team}")

        whatDo = [ACTION_PASS]

        if moves:
            whatDo.append(ACTION_MOVE)
        if shoots:
            whatDo.append(ACTION_ATTACK)

        # agent chooses type of action
        toa = np.random.choice(whatDo)

        actions = []

        if toa == ACTION_PASS:
            actions = [Pass(self.team, f)]

        if toa == ACTION_MOVE:
            actions = moves

        if toa == ACTION_ATTACK:
            actions = shoots

        return np.random.choice(actions)

    def chooseResponse(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        # choose to respond or not
        if not np.random.choice([True, False]):
            raise ValueError('no response given')

        # choose which figures that can still respond will respond
        figures = state.getFiguresRespondatable(self.team)
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
