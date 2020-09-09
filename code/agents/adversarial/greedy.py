"""This agent is an adaptation from the GreedyAgent in the main project source code."""
import logging
import math
from utils.copy import deepcopy
from typing import Tuple, Any, List

import numpy as np

from agents import Player
from agents.adversarial.probabilities import probabilityOfSuccessfulResponseAccumulated, probabilityOfSuccessfulAttack
from agents.adversarial.scores import evaluateBoard, evaluateState
from core import GM
from core.actions import Action
from core.const import RED
from core.figures import Figure
from core.game.board import GameBoard
from core.game.state import GameState
from utils.coordinates import to_cube


class GreedyAgent(Player):

    def __init__(self, team: str):
        super().__init__('GreedyAgent', team)

        self.maximize: bool = self.team == RED
        self.boardValues = None

    def checkBoardValues(self, board: GameBoard):
        if self.boardValues is None:
            self.boardValues = evaluateBoard(board, self.team)

    def scorePass(self, board: GameBoard, state: GameState, figure: Figure) -> Tuple[float, Action]:
        action = GM.actionPass(figure)
        s, _ = GM.activate(board, state, action)
        return evaluateState(self.boardValues, s), action

    def scoreMove(self, board: GameBoard, state: GameState, figure: Figure) -> List[Tuple[float, Action]]:
        scores = []
        for action in GM.buildMovements(board, state, figure):
            # effect of action without enemy response
            s1, _ = GM.activate(board, state, action)
            noResponseScore = evaluateState(self.boardValues, s1)

            # effect of action with enemy response killing the unit
            s2, _ = GM.activate(board, state, action)
            s2.getFigure(action).killed = True
            responseScore = evaluateState(self.boardValues, s2)

            # accumulated probability of a successful response
            probResponseEffect = probabilityOfSuccessfulResponseAccumulated(board, state, action)

            score = (1 - probResponseEffect) * noResponseScore + probResponseEffect * responseScore
            scores.append((score, action))

            logging.debug(f'{self.team:5}: Current move score is {score}')

        return scores

    def scoreAttack(self, board: GameBoard, state: GameState, figure: Figure) -> List[Tuple[float, Action]]:
        scores = []

        # action does not have effect
        sNoEffect = evaluateState(self.boardValues, state)

        for action in GM.buildAttacks(board, state, figure):
            # action have effect
            s1, _ = GM.activate(board, state, action, True)
            sEffect = evaluateState(self.boardValues, s1)
            pEffect = probabilityOfSuccessfulAttack(board, state, action)

            # effect of action with enemy response killing the unit
            s2, _ = GM.activate(board, state, action)
            s2.getFigure(action).killed = True
            sRespEffect = evaluateState(self.boardValues, s2)

            # accumulated probability of a successful response
            pRespEffect = probabilityOfSuccessfulResponseAccumulated(board, state, action)

            score = pEffect * sEffect + (1 - pEffect) * (pRespEffect * sRespEffect + (1 - pRespEffect) * sNoEffect)
            scores.append((score, action))

            logging.debug(f'{self.team:5}: Current attack score is {score}')

        return scores

    def scoreResponse(self, board: GameBoard, state: GameState, figure: Figure,
                      sNoEffect: float) -> List[Tuple[float, Action]]:
        scores = []

        for action in GM.buildResponses(board, state, figure):
            # action have effect
            s1, _ = GM.activate(board, state, action, True)
            sEffect = evaluateState(self.boardValues, s1)
            pEffect = probabilityOfSuccessfulAttack(board, state, action)

            score = pEffect * sEffect + (1 - pEffect) * sNoEffect
            scores.append((score, action))

            logging.debug(f'{self.team:5}: Current response score is {score}')

        return scores

    def opt(self, scores) -> Tuple[float, Any]:
        max_value = -math.inf
        min_value = math.inf
        max_action = None
        min_action = None

        # search for best score
        for score, action in scores:
            if score > max_value:
                max_value = score
                max_action = action
            if score < min_value:
                min_value = score
                min_action = action

        if self.maximize:
            return max_value, max_action
        return min_value, min_action

    def chooseAction(self, board: GameBoard, state: GameState) -> Action:
        self.checkBoardValues(board)

        scores = []

        # compute all scores for possible actions for each available unit
        for figure in state.getFiguresCanBeActivated(self.team):
            scores.append(self.scorePass(board, state, figure))
            scores += self.scoreMove(board, state, figure)
            scores += self.scoreAttack(board, state, figure)

        # search for action with best score
        score, action = self.opt(scores)
        logging.info(f'{self.team:5}: {action} ({score})')
        return action

    def chooseResponse(self, board: GameBoard, state: GameState) -> Action:
        if not self.boardValues:
            self.boardValues = evaluateBoard(board, self.team)

        # action does not have effect
        sNoEffect = evaluateState(self.boardValues, state)

        scores = [
            # do not respond
            (sNoEffect, None)
        ]
        # compute all scores for possible responses
        for figure in state.getFiguresCanBeActivated(self.team):
            scores += self.scoreResponse(board, state, figure, sNoEffect)

        if len(scores) == 1:
            raise ValueError('no response given or available')

        # search for action with best score
        score, action = self.opt(scores)
        logging.info(f'{self.team:5}: {action} ({score})')

        if not action:
            raise ValueError('no response given')

        return action

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        self.checkBoardValues(board)

        # select area
        x, y = np.where(board.placement_zone[self.team] > 0)
        figures = state.getFigures(self.team)

        # choose groups of random positions
        indices = [np.random.choice(len(x), size=len(figures), replace=False) for _ in range(100)]

        scores = []
        s = deepcopy(state)

        for i in range(len(indices)):
            # select a group of positions
            group = indices[i]
            for j in range(len(group)):
                # move each unit to its position
                figure = figures[j]
                dst = to_cube((x[group[j]], y[group[j]]))
                s.moveFigure(figure, figure.position, dst)

            score = evaluateState(self.boardValues, s)
            scores.append((score, group))

        # choose the better group
        score, group = self.opt(scores)

        for j in range(len(group)):
            figure = figures[j]
            dst = to_cube((x[group[j]], y[group[j]]))
            state.moveFigure(figure, dst=dst)

        logging.info(f'{self.team:5}: placed his troops in {group} ({score})')

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        if not self.boardValues:
            self.boardValues = evaluateBoard(board, self.team)

        colors = list(state.choices[self.team].keys())
        scores = []

        for color in colors:
            s = deepcopy(state)
            s.choose(self.team, color)

            score = evaluateState(self.boardValues, s)
            scores.append((score, color))

        score, color = self.opt(scores)
        state.choose(self.team, color)

        logging.info(f'{self.team:5}: choose positions color {color}')
