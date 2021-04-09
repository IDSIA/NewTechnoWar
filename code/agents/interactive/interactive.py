import numpy as np

from agents import Agent
from core.actions import Action, Response
from core.const import RED, BLUE
from core.game import GameBoard, GameState
from core.utils.coordinates import Hex


class Human(Agent):
    """
    This class works with the date from the web service.
    """

    __slots__ = ['next_action', 'next_response', 'color', 'place']

    def __init__(self, team: str):
        """
        :param team:    color of the team
        """
        super().__init__('Human', team)
        self.next_action: Action or None = None
        self.next_response: Response or None = None

        self.color: str = ''
        self.place: dict = {}

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
        for figure in state.getFigures(self.team):
            if figure.index in self.place:
                dst = self.place[figure.index]
                state.moveFigure(figure, figure.position, dst)

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        if self.color == '':
            colors = list(state.choices[self.team].keys())
            self.color = np.random.choice(colors)

        state.choose(self.team, self.color)

    def nextAction(self, board: GameBoard, state: GameState, data: dict) -> None:
        """
        Parse the given data structure in order to get the next action.

        :param board:       board of the game
        :param state:       current state of the game
        :param data:        data received from a human through the web interface
        """
        action = data['action']
        self._clear()

        if action == 'choose':
            self.color = data['color']
            return

        if action == 'place':
            idx = int(data['idx'])
            x = int(data['x'])
            y = int(data['y'])
            pos = Hex(x, y).cube()

            self.place[idx] = pos
            return

        if action == 'pass':
            if 'idx' in data and data['team'] == self.team:
                idx = int(data['idx'])
                figure = state.getFigureByIndex(self.team, idx)
                self.next_action = self.gm.actionPassFigure(figure)
            elif data['step'] == 'respond':
                self.next_action = self.gm.actionPassResponse(self.team)
            else:
                self.next_action = self.gm.actionPassTeam(self.team)
            return

        idx = int(data['idx'])
        x = int(data['x'])
        y = int(data['y'])
        pos = Hex(x, y).cube()

        figure = state.getFigureByIndex(self.team, idx)

        if figure.responded and data['step'] == 'respond':
            raise ValueError('Unit has already responded!')

        if figure.activated and data['step'] in ('round', 'move'):
            raise ValueError('Unit has already been activated!')

        if action == 'move':
            fs = state.getFiguresByPos(self.team, pos)
            for transport in fs:
                if transport.canTransport(figure):
                    self.next_action = self.gm.actionLoadInto(board, state, figure, transport)
                    return

            self.next_action = self.gm.actionMove(board, state, figure, destination=pos)
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

            self.next_action = self.gm.actionAttack(board, state, figure, target, weapon)
            self.next_response = self.gm.actionRespond(board, state, figure, target, weapon)

        # TODO: implement smoke
