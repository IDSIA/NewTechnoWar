from agents.players import PlayerDummy
from core import RED, BLUE
from core.actions import Action, Respond
from core.game.board import GameBoard
from core.game.manager import GameManager
from core.game.state import GameState
from utils.coordinates import to_cube


class Human(PlayerDummy):
    __slots__ = ['next_action', 'next_response']

    def __init__(self, team: str):
        super().__init__(team)
        self.name = 'Human'
        self.next_action: Action or None = None
        self.next_response: Respond or None = None

    def _clear(self):
        self.next_action = None
        self.next_response = None

    def chooseAction(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        a = self.next_action
        self._clear()
        if not a:
            raise ValueError('no action taken')
        return a

    def chooseResponse(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        r = self.next_response
        self._clear()
        if not r:
            raise ValueError('no response taken')
        return r

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        # TODO
        super().placeFigures(board, state)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        # TODO
        super().chooseFigureGroups(board, state)

    def nextAction(self, board: GameBoard, state: GameState, gm: GameManager, data: dict) -> None:
        action = data['action']
        self._clear()

        if action == 'pass':
            if 'idx' in data and data['team'] == self.team:
                idx = int(data['idx'])
                transport = state.getFigureByIndex(self.team, idx)
                self.next_action = gm.actionPass(transport)
            return

        idx = int(data['idx'])
        x = int(data['x'])
        y = int(data['y'])
        pos = to_cube((x, y))

        figure = state.getFigureByIndex(self.team, idx)

        if action == 'move':
            fs = state.getFiguresByPos(self.team, pos)
            for transport in fs:
                if transport.canTransport(figure):
                    self.next_action = gm.actionLoadInto(board, figure, transport)
                    return

            self.next_action = gm.actionMove(board, figure, destination=pos)
            return

        if action == 'attack':
            w = data['weapon']
            weapon = figure.weapons[w]

            if 'targetTeam' in data:
                targetTeam = data['targetTeam']
                targetIdx = int(data['targetIdx'])
                target = state.getFigureByIndex(targetTeam, targetIdx)

            else:
                otherTeam = BLUE if self.team == RED else RED
                target = state.getFiguresByPos(otherTeam, pos)[0]  # TODO: get unit based on index or weapon target type

            self.next_action = gm.actionAttack(board, state, figure, target, weapon)
            self.next_response = gm.actionRespond(board, state, figure, target, weapon)

        # TODO: implement smoke
