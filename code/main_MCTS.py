import os
import logging

from datetime import datetime

import numpy as np

from core.const import RED, BLUE
from core.game.manager import GameManager
from core.scenarios import buildScenario
from core.templates import buildFigure
from core.game import GameBoard, GameState, GoalReachPoint, GoalDefendPoint, GoalMaxTurn
from core.utils.coordinates import Hex
from utils.setup_logging import setup_logging
from utils import dotdict

# from NNet import NNetWrapper as nn
from agents.reinforced import NNetWrapper as nn, Coach, MCTS

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

setup_logging()
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    # random seed for repeatability
    seed = 151775519

    # the available maps depend on the current config files
    # board, state = buildScenario('TestBench')

    # this is a small dummy scenario for testing purposes
    shape = (5, 5)
    board = GameBoard(shape)
    state = GameState(shape)

    terrain = np.zeros(shape, 'uint8')
    terrain[:, 2] = 3  # forest
    board.addTerrain(terrain)

    goal = [Hex(4, 4)]
    board.addObjectives(
        GoalReachPoint(RED, shape, goal),
        GoalDefendPoint(BLUE, RED, shape, goal),
        GoalMaxTurn(BLUE, 4),
    )

    state.addFigure(
        buildFigure('Infantry', (0, 0), RED, 'r_inf_1'),
        buildFigure('Infantry', (0, 4), BLUE, 'b_inf_1'),
    )

    # this is to avoid initialization step
    gm = GameManager(seed)
    gm.update(state)

    now = datetime.now().strftime('%Y%m%d.%H%M%S')

    args = dotdict({
        'numIters': 20,  # 1000,
        'numEps': 10,  # 100,             # Number of complete self-play games to simulate during a new iteration.
        'tempThreshold': 15,
        'maxlenOfQueue': 10,  # 200000,   # Number of game examples to train the neural networks.
        'numMCTSSims': 30,  # 30, #25,    # Number of games moves for MCTS to simulate.
        'cpuct': 1,
        'checkpoint': f'./temp.{now}/',
        'load_model': False,
        'load_folder_file': '/models',
        'numItersForTrainExamplesHistory': 1,  # 20
        'maxMoveNoResponseSize': 1351,
        'maxAttackSize': 288,
        'maxWeaponPerFigure': 8,
        'maxFigurePerScenario': 6,
        'seed': seed,
    })

    if args.load_model:
        logger.info('Loading checkpoint "%s/%s"...', args.load_folder_file)
        # nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])
        nn.load_checkpoint(args.load_folder_file)

    else:
        # mcts = MCTS(board, state, RED, args)
        # pi = mcts.getActionProb(board, state, RED, temp=1)
        # print(len(pi), len(np.where(np.array(pi)>0)[0]), np.where(np.array(pi)>0)[0], [pi[x] for x in np.where(np.array(pi)>0)[0]])

        nnet_RED_Act = nn(board.shape, seed)
        nnet_RED_Res = nn(board.shape, seed)
        nnet_BLUE_Act = nn(board.shape, seed)
        nnet_BLUE_Res = nn(board.shape, seed)

        team = RED
        moveType = "Action"

        logger.info('Loading the Coach...')

        c = Coach(board, state, team, moveType, nnet_RED_Act, nnet_RED_Res, nnet_BLUE_Act, nnet_BLUE_Res, args)

        if args.load_model:
            logger.info("Loading 'trainExamples' from file...")
            c.loadTrainExamples()

        logger.info('Starting the learning process')
        c.learn()
