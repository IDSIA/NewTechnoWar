import argparse
import os
import logging
import sys

from datetime import datetime

import numpy as np
import ray

from core.const import RED, BLUE
from core.game.goals import GoalEliminateOpponent
from core.scenarios import buildScenario
from core.templates import buildFigure
from core.game import GameBoard, GameState, GoalReachPoint, GoalDefendPoint, GoalMaxTurn
from core.utils.coordinates import Hex
from utils.setup_logging import setup_logging

# from NNet import NNetWrapper as nn
from agents.reinforced import NNetWrapper as nn, Coach

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

setup_logging()
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    os.environ['RAY_DISABLE_IMPORT_WARNING'] = '1'
    num_cores = os.cpu_count() - 1

    p = argparse.ArgumentParser()
    p.add_argument('cores', help="max num of cores to use", type=int, default=num_cores)
    args = p.parse_args()

    logger.info("Using %s cores", args.cores)
    ray.init(num_cpus=args.cores)

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
        GoalEliminateOpponent(RED, BLUE),
        GoalEliminateOpponent(BLUE, RED),
    )

    state.addFigure(
        buildFigure('Infantry', (0, 0), RED, 'r_inf_1'),
        buildFigure('Infantry', (0, 4), BLUE, 'b_inf_1'),
    )

    # training arguments setup
    now = datetime.now().strftime('%Y%m%d.%H%M%S')

    # parameters for coach and MCTS
    epochs = 5  # number of epochs for training
    num_iters = 100  # 1000,
    num_eps = 10  # 100,             # Number of complete self-play games to simulate during a new iteration.
    max_queue_len = 1000  # 200000,  # Number of game examples to train the neural networks.
    num_MCTS_sims = 30  # 30, #25,   # Number of games moves for MCTS to simulate.
    n_it_tr_examples_history = 20  # 1  # 20
    checkpoint = f'./temp.{now}/'

    parallel = True,  # put true to use ray and parallel execution of episodes
    load_model = False

    red_act = nn(board.shape, seed, epochs=epochs)
    red_res = nn(board.shape, seed, epochs=epochs)
    blue_act = nn(board.shape, seed, epochs=epochs)
    blue_res = nn(board.shape, seed, epochs=epochs)

    logger.info('Loading the Coach...')

    c = Coach(board, state, red_act, red_res, blue_act, blue_res, seed=seed, num_iters=num_iters, num_eps=num_eps, max_queue_len=max_queue_len,
              num_MCTS_sims=num_MCTS_sims, folder_checkpoint=checkpoint, num_it_tr_examples_history=n_it_tr_examples_history, parallel=parallel)

    if load_model:
        logger.info("Loading 'trainExamples' from file...")
        c.loadTrainExamples()

    logger.info('Starting the learning process')
    c.learn()
