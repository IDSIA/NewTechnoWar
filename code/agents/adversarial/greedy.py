"""This agent is an adaptation from the GreedyAgent in the main project source code."""
import logging
import math
from copy import deepcopy
from typing import List, Tuple, Any

import numpy as np

from agents.adversarial.probabilities import probabilityOfSuccessfulResponseAccumulated, probabilityOfSuccessfulAttack
from agents import Player
from core import RED, BLUE
from core.actions import Action
from core.figures import Figure
from core.game.board import GameBoard
from core.game.manager import GameManager
from core.game.state import GameState
from utils.coordinates import to_cube, cube_distance, cube_to_hex


class GreedyAgent(Player):

    def __init__(self, team: str):
        super().__init__('GreedyAgent', team)

        self.maximize: bool = self.team == RED
        self.boardValues = None

    def evaluateBoard(self, board: GameBoard):
        boardValues = np.zeros(board.shape)
        objs = board.getObjectivesPositions(self.team)

        for x, y in np.ndindex(board.shape):
            xy = to_cube((x, y))
            for o in objs:
                boardValues[x, y] = cube_distance(xy, o)

        maxBV = np.max(boardValues)

        for x, y in np.ndindex(board.shape):
            boardValues[x, y] = 1 - boardValues[x, y] / maxBV

        for o in objs:
            boardValues[cube_to_hex(o)] = 5

        return boardValues

    def evaluateState(self, state: GameState):
        value = 0
        bv = self.boardValues

        for figure in state.getFigures(RED):
            if not figure.killed:
                value += 0.2 * bv[cube_to_hex(figure.position)] + 1

        for figure in state.getFigures(BLUE):
            if not figure.killed:
                value += 0.2 * bv[cube_to_hex(figure.position)] + 1

        # if state.turn >= self.board['totalTurns']: TODO: add penalty to endgame
        #     return -5

        return value

    def scorePass(self, gm: GameManager, board: GameBoard, state: GameState, figure: Figure) -> Tuple[float, Action]:
        action = gm.actionPass(figure)
        s, _ = gm.activate(board, state, action)
        return self.evaluateState(s), action

    def scoreMove(self,
                  gm: GameManager, board: GameBoard, state: GameState, figure: Figure) -> List[Tuple[float, Action]]:
        scores = []
        for action in gm.buildMovements(board, state, figure):
            # effect of action without enemy response
            s1, _ = gm.activate(board, state, action)
            noResponseScore = self.evaluateState(s1)

            # effect of action with enemy response killing the unit
            s2, _ = gm.activate(board, state, action)
            s2.getFigure(action).killed = True
            responseScore = self.evaluateState(s2)

            # accumulated probability of a successful response
            probResponseEffect = probabilityOfSuccessfulResponseAccumulated(gm, board, state, action)

            score = (1 - probResponseEffect) * noResponseScore + probResponseEffect * responseScore
            scores.append((score, action))

            logging.debug(f'{self.team:5}: Current move score is {score}')

        return scores

    def scoreAttack(self,
                    gm: GameManager, board: GameBoard, state: GameState, figure: Figure) -> List[Tuple[float, Action]]:
        scores = []

        # action does not have effect
        sNoEffect = self.evaluateState(state)

        for action in gm.buildAttacks(board, state, figure):
            # action have effect
            s1, _ = gm.activate(board, state, action, True)
            sEffect = self.evaluateState(s1)
            pEffect = probabilityOfSuccessfulAttack(gm, board, state, action)

            # effect of action with enemy response killing the unit
            s2, _ = gm.activate(board, state, action)
            s2.getFigure(action).killed = True
            sRespEffect = self.evaluateState(s2)

            # accumulated probability of a successful response
            pRespEffect = probabilityOfSuccessfulResponseAccumulated(gm, board, state, action)

            score = pEffect * sEffect + (1 - pEffect) * (pRespEffect * sRespEffect + (1 - pRespEffect) * sNoEffect)
            scores.append((score, action))

            logging.debug(f'{self.team:5}: Current attack score is {score}')

        return scores

    def scoreResponse(self, gm: GameManager, board: GameBoard, state: GameState, figure: Figure,
                      sNoEffect: float) -> List[Tuple[float, Action]]:
        scores = []

        for action in gm.buildResponses(board, state, figure):
            # action have effect
            s1, _ = gm.activate(board, state, action, True)
            sEffect = self.evaluateState(s1)
            pEffect = probabilityOfSuccessfulAttack(gm, board, state, action)

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

    def chooseAction(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        if self.boardValues is None:
            self.boardValues = self.evaluateBoard(board)

        scores = []

        # compute all scores for possible actions for each available unit
        for figure in state.getFiguresCanBeActivated(self.team):
            scores.append(self.scorePass(gm, board, state, figure))
            scores += self.scoreMove(gm, board, state, figure)
            scores += self.scoreAttack(gm, board, state, figure)

        # search for action with best score
        score, action = self.opt(scores)
        logging.info(f'{self.team:5}: {action} ({score})')
        return action

    def chooseResponse(self, gm: GameManager, board: GameBoard, state: GameState) -> Action:
        if not self.boardValues:
            self.boardValues = self.evaluateBoard(board)

        # action does not have effect
        sNoEffect = self.evaluateState(state)

        scores = [
            # do not respond
            (sNoEffect, None)
        ]
        # compute all scores for possible responses
        for figure in state.getFiguresCanBeActivated(self.team):
            scores += self.scoreResponse(gm, board, state, figure, sNoEffect)

        if len(scores) == 1:
            raise ValueError('no response given or available')

        # search for action with best score
        score, action = self.opt(scores)
        logging.info(f'{self.team:5}: {action} ({score})')

        if not action:
            raise ValueError('no response given')

        return action

    def placeFigures(self, board: GameBoard, state: GameState) -> None:
        if not self.boardValues:
            self.boardValues = self.evaluateBoard(board)

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
                s.moveFigure(self.team, figure, figure.position, dst)

            score = self.evaluateState(s)
            scores.append((score, group))

        # choose the better group
        score, group = self.opt(scores)

        for j in range(len(group)):
            figure = figures[j]
            dst = to_cube((x[group[j]], y[group[j]]))
            state.moveFigure(self.team, figure, dst=dst)

        logging.info(f'{self.team:5}: placed his troops in {group} ({score})')

    def chooseFigureGroups(self, board: GameBoard, state: GameState) -> None:
        if not self.boardValues:
            self.boardValues = self.evaluateBoard(board)

        colors = list(state.choices[self.team].keys())
        scores = []

        for color in colors:
            s = deepcopy(state)
            s.choose(self.team, color)

            score = self.evaluateState(s)
            scores.append((score, color))

        score, color = self.opt(scores)
        state.choose(self.team, color)

        logging.info(f'{self.team:5}: choose positions color {color}')
