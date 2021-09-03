import logging
from utils.setup_logging import setup_logging
setup_logging()

import argparse
import os
import json

from datetime import datetime
from typing import Tuple

import numpy as np
import ray
import torch

from core.const import RED, BLUE
from core.game.goals import GoalEliminateOpponent
from core.scenarios import buildScenario
from core.templates import buildFigure
from core.game import GameBoard, GameState, GoalReachPoint, GoalDefendPoint, GoalMaxTurn
from core.utils.coordinates import Hex

# from NNet import NNetWrapper as nn
from agents.reinforced import ModelWrapper, Coach

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

logger = logging.getLogger('agents')


def scenario5x5() -> Tuple[GameBoard, GameState]:
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

    while True:
        yield board, state


def scenario10x10() -> Tuple[GameBoard, GameState]:
    shape = (10, 10)
    board = GameBoard(shape)
    state = GameState(shape)

    terrain = np.zeros(shape, 'uint8')
    terrain[:, 2] = 3  # forest
    terrain[:, 7] = 3  # forest
    terrain[5, :] = 1  # road
    board.addTerrain(terrain)

    goal = [Hex(5, 5)]
    board.addObjectives(
        GoalReachPoint(RED, shape, goal),
        GoalDefendPoint(BLUE, RED, shape, goal),
        GoalMaxTurn(BLUE, 6),
        GoalEliminateOpponent(RED, BLUE),
        GoalEliminateOpponent(BLUE, RED),
    )

    state.addFigure(
        buildFigure('Infantry', (4, 0), RED, 'r_inf_1'),
        buildFigure('Infantry', (6, 0), RED, 'r_inf_2'),
        buildFigure('Infantry', (4, 9), BLUE, 'b_inf_1'),
        buildFigure('Infantry', (6, 9), BLUE, 'b_inf_2'),
    )

    while True:
        yield board, state


def scenarioRandom10x10(seed: int = 0, s: int = -1) -> Tuple[GameBoard, GameState]:
    seed_gen = np.random.default_rng(seed)

    shape = (10, 10)

    generate_s = s == -1

    while True:
        if generate_s:
            s = seed_gen.integers(low=100000000, high=1000000000)
        logger.info('random seed=%s s=%s', seed, s)

        r = np.random.default_rng(s)

        board = GameBoard(shape, gen_seed=s)
        state = GameState(shape)

        terrain = np.zeros(shape, 'uint8')

        # trees
        if r.random() > .8:
            terrain[:, 2] = 2  # tree
        if r.random() > .5:
            terrain[:, 3] = 2  # tree
        if r.random() > .5:
            terrain[:, 5] = 2  # tree
        if r.random() > .8:
            terrain[:, 7] = 2  # tree

        # buildings
        if r.random() > .3:
            for _ in range(r.integers(low=1, high=5)):
                x, y = r.integers(low=0, high=10, size=2)
                terrain[x, y] = 5

        # forests
        if r.random() > .4:
            for _ in range(r.integers(low=1, high=5)):
                x, y = r.integers(low=1, high=9, size=2)
                terrain[x, y] = 3
                terrain[x+1, +1] = 3
                terrain[x+1, y] = 3
                terrain[x, y+1] = 3
                if r.random() > .5:
                    terrain[x, y-1] = 3
                if r.random() > .5:
                    terrain[x-1, y-1] = 3
                if r.random() > .5:
                    terrain[x-1, y] = 3

        if r.random() > .6:
            terrain[2, :] = 1  # road vertical
        if r.random() > .4:
            terrain[5, :] = 1  # road vertical
        if r.random() > .6:
            terrain[8, :] = 1  # road vertical
        if r.random() > .5:
            terrain[:, 5] = 1  # road horizontal
        if r.random() > .6:
            terrain[:, 3] = 1  # road horizontal
        if r.random() > .6:
            terrain[:, 8] = 1  # road horizontal

        board.addTerrain(terrain)

        x, y = r.integers(low=3, high=8, size=2)
        max_turns = r.integers(low=5, high=12)

        goal = [Hex(x, y)]
        board.addObjectives(
            GoalReachPoint(RED, shape, goal),
            GoalDefendPoint(BLUE, RED, shape, goal),
            GoalMaxTurn(BLUE, max_turns),
            GoalEliminateOpponent(RED, BLUE),
            GoalEliminateOpponent(BLUE, RED),
        )

        pos_red_x = r.choice(range(0, 10), 4)
        pos_red_y = r.choice(range(0, 3), 4)
        pos_blue_x = r.choice(range(0, 10), 4)
        pos_blue_y = r.choice(range(7, 10), 4)

        figures_red = [
            buildFigure('Infantry', (pos_red_x[0],  pos_red_y[0]),  RED,  'r_inf_1'),
            buildFigure('Infantry', (pos_red_x[1],  pos_red_y[1]),  RED,  'r_inf_2'),
            buildFigure('Tank',     (pos_red_x[2],  pos_red_y[2]),  RED,  'r_tank_1'),
            buildFigure('Tank',     (pos_red_x[3],  pos_red_y[3]),  RED,  'r_tank_2'),
        ]
        figures_blue = [
            buildFigure('Infantry', (pos_blue_x[0], pos_blue_y[0]), BLUE, 'b_inf_1'),
            buildFigure('Infantry', (pos_blue_x[1], pos_blue_y[1]), BLUE, 'b_inf_2'),
            buildFigure('Tank',     (pos_blue_x[2], pos_blue_y[2]), BLUE, 'b_tank_1'),
            buildFigure('Tank',     (pos_blue_x[3], pos_blue_y[3]), BLUE, 'b_tank_2'),
        ]

        n_red = r.choice(range(1, len(figures_red)))
        n_blue = r.choice(range(1, len(figures_blue)))

        choosen_red = r.choice(figures_red, n_red, replace=False)
        choosen_blue = r.choice(figures_blue, n_blue, replace=False)

        state.addFigure(*choosen_red)
        state.addFigure(*choosen_blue)

        yield board, state


if __name__ == '__main__':
    os.environ['RAY_DISABLE_IMPORT_WARNING'] = '1'

    NUM_CORES: int = max(1, os.environ.get('NUM_CORES', os.cpu_count() - 1))
    NUM_GPUS: int = os.environ.get('NUM_GPUS', torch.cuda.device_count())
    SEED = 151775519
    EPOCHS = 5

    # parameters for coach and MCTS
    NUM_ITERS = 100  # 1000,
    NUM_EPS = 10  # 100,             # Number of complete self-play games to simulate during a new iteration.
    MAX_QUEUE_LEN = 1000  # 200000,  # Number of game examples to train the neural networks.
    NUM_MCTS_SIMS = 30  # 30, #25,   # Number of games moves for MCTS to simulate.
    N_IT_TR_EXAMPLES_HISTORY = 20  # 1  # 20
    CHECKPOINT_DIR = './temp'

    p = argparse.ArgumentParser()
    p.add_argument('-c', '--cpus', type=int, default=NUM_CORES, help=f'default: {NUM_CORES}\tmax num of cores to use')
    p.add_argument('-g', '--gpus', type=int, default=NUM_GPUS, help=f'default: {NUM_GPUS}\tmax num of gpus to use')
    p.add_argument('-s', '--seed', type=int, default=SEED, help=f'default: {SEED}\trandom seed to use')
    p.add_argument('-e', '--epochs', type=int, default=EPOCHS, help=f'default: {EPOCHS}\ttraining epochs for nn')
    p.add_argument('-i', '--iters', type=int, default=NUM_ITERS, help=f'default: {NUM_ITERS}\tmax num of iterations')
    p.add_argument('-j', '--eps', type=int, default=NUM_EPS, help=f'default: {NUM_EPS}\tmax num of episodes for each iteration')
    p.add_argument('-q', '--qlen', type=int, default=MAX_QUEUE_LEN, help=f'default: {MAX_QUEUE_LEN}\tmax num of episodes to train the nn')
    p.add_argument('-m', '--sims', type=int, default=NUM_MCTS_SIMS, help=f'default: {NUM_MCTS_SIMS}\tmax num of move for MCTS simulations')
    p.add_argument('-x', '--trex', type=int, default=N_IT_TR_EXAMPLES_HISTORY, help=f'default: {N_IT_TR_EXAMPLES_HISTORY}\t')
    p.add_argument('-d', '--dir', type=str, default=CHECKPOINT_DIR, help=f'default: {CHECKPOINT_DIR}\tcheckpoint directory')
    p.add_argument('-l', '--load', default=False, action='store_true', help=f'{""}\tif set, continue with already trained models in --dir folder')
    p.add_argument('-s5', '--scenario-5x5', default=False, dest='s5', action='store_true', help=f'{""}\tuse 5x5 scenario')
    p.add_argument('-s10', '--scenario-10x10', default=False, dest='s10', action='store_true', help=f'{""}\tuse 10x10 scenario')
    p.add_argument('-r10', '--scenario-random-10x10', default=False, dest='r10', action='store_true', help=f'{""}\tuse 10x10 scenario with random init')
    args = p.parse_args()

    logger.info("Using %s cores", args.cpus)
    logger.info("Using %s gpus", args.gpus)

    ray.init(num_cpus=args.cpus, num_gpus=args.gpus)

    # if true,use ray and parallel execution of episodes
    parallel = args.cpus > 1
    # random seed for repeatability
    seed = args.seed

    # the available maps depend on the current config files
    # board, state = buildScenario('TestBench')

    # this is a small dummy scenario for testing purposes
    gen = None
    shape = None
    if args.s5:
        gen = scenario5x5()
        shape = (5, 5)
    if args.s10:
        gen = scenario10x10()
        shape = (10, 10)
    if args.r10:
        gen = scenarioRandom10x10(seed)
        shape = (10, 10)

    if not gen:
        logger.error("no scenario selected")
        exit(1)

    # training arguments setup
    now = datetime.now().strftime('%Y%m%d.%H%M%S')

    epochs = args.epochs
    num_iters = args.iters
    num_eps = args.eps
    max_queue_len = args.qlen
    num_MCTS_sims = args.sims
    n_it_tr_examples_history = args.trex
    checkpoint = f'{args.dir}.{now}/'
    load_model = args.load

    os.makedirs(checkpoint, exist_ok=True)
    with open(os.path.join(checkpoint, f'config.{now}.json'), 'w') as f:
        json.dump({
            'start': now,
            '5x5': args.s5,
            '10x10': args.s10,
            'random10x10': args.r10,
            'cpus': args.cpus,
            'gpus': args.gpus,
            'seed': seed,
            'parallel': parallel,
            'epochs': epochs,
            'num_iters': num_iters,
            'num_eps': num_eps,
            'max_queue_len': max_queue_len,
            'num_MCTS_sims': num_MCTS_sims,
            'n_it_tr_examples_history': n_it_tr_examples_history,
            'checkpoint': checkpoint,
        }, f)

    red_act = ModelWrapper(shape, seed, epochs=epochs)
    red_res = ModelWrapper(shape, seed, epochs=epochs)
    blue_act = ModelWrapper(shape, seed, epochs=epochs)
    blue_res = ModelWrapper(shape, seed, epochs=epochs)

    logger.info('Loading the Coach...')

    c = Coach(gen, red_act, red_res, blue_act, blue_res, seed=seed, num_iters=num_iters, num_eps=num_eps, max_queue_len=max_queue_len,
              num_MCTS_sims=num_MCTS_sims, folder_checkpoint=checkpoint, num_it_tr_examples_history=n_it_tr_examples_history, parallel=parallel)

    if load_model:
        logger.info("Loading 'trainExamples' from file...")
        c.loadTrainExamples()

    logger.info('Starting the learning process')
    c.learn()
