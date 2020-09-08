from agents import PlayerDummy
from core import GM
from core.actions import Action, Respond
from core.const import RED, BLUE
from core.game.board import GameBoard
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

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        a = self.next_action
        self._clear()
        if not a:
            raise ValueError('no action taken')
        return a

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
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

    def nextAction(self, board: GameBoard, state: GameState, data: dict) -> None:
        action = data['action']
        self._clear()

        if action == 'pass':
            if 'idx' in data and data['team'] == self.team:
                idx = int(data['idx'])
                figure = state.getFigureByIndex(self.team, idx)
                self.next_action = GM.actionPass(figure)
            return

        idx = int(data['idx'])
        x = int(data['x'])
        y = int(data['y'])
        pos = to_cube((x, y))

        figure = state.getFigureByIndex(self.team, idx)

        if figure.responded and data['step'] == 'respond':
            raise ValueError('Unit has already responded!')

        if figure.activated and data['step'] in ('round', 'move'):
            raise ValueError('Unit has already been activated!')

        if action == 'move':
            fs = state.getFiguresByPos(self.team, pos)
            for transport in fs:
                if transport.canTransport(figure):
                    self.next_action = GM.actionLoadInto(board, figure, transport)
                    return

            self.next_action = GM.actionMove(board, figure, destination=pos)
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

            self.next_action = GM.actionAttack(board, state, figure, target, weapon)
            self.next_response = GM.actionRespond(board, state, figure, target, weapon)

        # TODO: implement smoke
