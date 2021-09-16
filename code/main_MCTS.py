import logging
from utils.setup_logging import setup_logging
setup_logging()

import argparse
import os
import pickle
import json

from datetime import datetime
from typing import Tuple

import numpy as np
import ray
import torch

from core.const import RED, BLUE
from core.game.goals import GoalEliminateOpponent
from core.scenarios.generators import scenarioRandom10x10, scenarioRandom5x5
from core.templates import buildFigure
from core.game import GameBoard, GameState, GoalReachPoint, GoalDefendPoint, GoalMaxTurn
from core.utils.coordinates import Hex

from agents import AlphaBetaAgent, GreedyAgent
from agents.reinforced import ModelWrapper, Coach, Trainer

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
os.environ['RAY_DISABLE_IMPORT_WARNING'] = '1'

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


if __name__ == '__main__':
    NOW = datetime.now().strftime('%Y%m%d.%H%M%S')

    NUM_CORES: int = max(1, os.environ.get('NUM_CORES', os.cpu_count() - 1))
    NUM_GPUS: int = os.environ.get('NUM_GPUS', torch.cuda.device_count())

    # parameters for coach and MCTS
    SEED: int = 151775519
    MAX_DEPTH: int = 100
    MAX_TR_EXAMPLES: int = 1000  # 200000,  # Number of game examples to train the neural networks.

    EPOCHS: int = 5
    NUM_ITERS: int = 100  # 1000,
    NUM_EPS: int = 10  # 100,             # Number of complete self-play games to simulate during a new iteration.
    NUM_MCTS_SIMS: int = 30  # 30, #25,   # Number of games moves for MCTS to simulate.

    CHECKPOINT_DIR: str = f'./temp.{NOW}'

    SUPPORT_RED: str or None = None
    SUPPORT_BLUE: str or None = None
    SUPPORT_HELP: float = 1.0
    SUPPORT_BOOST_PROB: float = 1.0

    # game parameters: TODO: drive by game files
    max_weapon_per_figure: int = 8
    max_figure_per_scenario: int = 6
    max_move_no_response_size: int = 1351
    max_attack_size: int = 288

    # unknown parameters...
    cpuct: int = 1
    temp_threshold: int = 15

    p = argparse.ArgumentParser()
    # resources
    p.add_argument('-c', '--cpus', type=int, default=NUM_CORES, help=f'default: {NUM_CORES}\tmax num of cores to use')
    p.add_argument('-g', '--gpus', type=int, default=NUM_GPUS, help=f'default: {NUM_GPUS}\tmax num of gpus to use')
    p.add_argument('-s', '--seed', type=int, default=SEED, help=f'default: {SEED}\trandom seed to use')
    # train parameters
    p.add_argument('-e', '--epochs', type=int, default=EPOCHS, help=f'default: {EPOCHS}\ttraining epochs for nn')
    p.add_argument('-i', '--iters', type=int, default=NUM_ITERS, help=f'default: {NUM_ITERS}\tmax num of iterations')
    p.add_argument('-j', '--episodes', type=int, default=NUM_EPS, help=f'default: {NUM_EPS}\tmax num of episodes for each iteration')
    p.add_argument('-q', '--qlen', type=int, default=MAX_TR_EXAMPLES, help=f'default: {MAX_TR_EXAMPLES}\tmax num of episodes to train the nn')
    p.add_argument('-w', '--dir', type=str, default=CHECKPOINT_DIR, help=f'default: {CHECKPOINT_DIR}\tcheckpoint directory')
    p.add_argument('-l', '--load', default=False, action='store_true', help=f'\tif set, continue with already trained models in --dir folder')
    p.add_argument('-a', '--accumulate', default=False, action='store_true', help=f'\tif set, accumulate training episodes')
    # MCTS parameters
    p.add_argument('-m', '--sims', type=int, default=NUM_MCTS_SIMS, help=f'default: {NUM_MCTS_SIMS}\tmax num of move for MCTS simulations')
    p.add_argument('-d', '--depth', type=int, default=MAX_DEPTH, help=f'{MAX_DEPTH}\tmax depth for MCTS tree exploration.')
    # scenarios
    p.add_argument('-s5', '--scenario-5x5', default=False, dest='s5', action='store_true', help=f'\tuse 5x5 scenario')
    p.add_argument('-r5', '--scenario-random-5x5', default=False, dest='r5', action='store_true', help=f'\tuse 5x5 scenario with random init')
    p.add_argument('-s10', '--scenario-10x10', default=False, dest='s10', action='store_true', help=f'\tuse 10x10 scenario')
    p.add_argument('-r10', '--scenario-random-10x10', default=False, dest='r10', action='store_true', help=f'\tuse 10x10 scenario with random init')
    # support assistants
    p.add_argument('-sar', '--support-red', default=SUPPORT_RED, dest='sar', help=f'\tUse a support agent (greedy or alphabeta) for red during episodes generation')
    p.add_argument('-sab', '--support-blue', default=SUPPORT_BLUE, dest='sab', help=f'\tUse a support agent (greedy or alphabeta) for blue during episodes generation')
    p.add_argument('-sh', '--support-help', type=float, default=SUPPORT_HELP, dest='shelp', help=f'default: {SUPPORT_HELP}\tpercentage of iterations with help (starting from first)')
    p.add_argument('-b', '--support-boost', type=float, default=SUPPORT_BOOST_PROB, dest='boost', help=f'default: {SUPPORT_BOOST_PROB}\tboost probability for support chosen actions')
    args = p.parse_args()

    logger.info("Using %s cores", args.cpus)
    logger.info("Using %s gpus", args.gpus)

    # if true,use ray and parallel execution of episodes
    parallel = args.cpus > 1
    if parallel:
        # ray.init(num_cpus=args.cpus, num_gpus=args.gpus)
        ray.init(num_cpus=args.cpus)

    # random seed for repeatability
    seed = args.seed

    # this is a small dummy scenario for testing purposes
    gen = None
    shape = None
    if args.s5:
        gen = scenario5x5()
        shape = (5, 5)
    if args.r5:
        gen = scenarioRandom5x5(seed)
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

    epochs = args.epochs
    num_iters = args.iters
    num_eps = args.episodes
    max_tr_examples = args.qlen
    num_MCTS_sims = args.sims
    checkpoint = args.dir
    load_models = args.load
    boost = args.boost
    max_depth = args.depth
    support_help = args.shelp

    os.makedirs(checkpoint, exist_ok=True)
    os.makedirs(os.path.join(checkpoint, 'models'), exist_ok=True)
    os.makedirs(os.path.join(checkpoint, 'episodes'), exist_ok=True)
    os.makedirs(os.path.join(checkpoint, 'metrics'), exist_ok=True)

    with open(os.path.join(checkpoint, f'config.{NOW}.json'), 'w') as f:
        json.dump({
            'start': NOW,
            '5x5': args.s5,
            '10x10': args.s10,
            'random5x5': args.r5,
            'random10x10': args.r10,
            'cpus': args.cpus,
            'gpus': args.gpus,
            'seed': seed,
            'parallel': parallel,
            'num_iters': num_iters,
            'num_eps': num_eps,
            'epochs': epochs,
            'max_tr_examples': max_tr_examples,
            'max_depth': max_depth,
            'num_MCTS_sims': num_MCTS_sims,
            'temp_threshold': temp_threshold,
            'max_weapon_per_figure': max_weapon_per_figure,
            'max_figure_per_scenario': max_figure_per_scenario,
            'max_move_no_response_size': max_move_no_response_size,
            'max_attack_size': max_attack_size,
            'checkpoint': checkpoint,
            'support_red': args.sar,
            'support_blue': args.sab,
            'boost_probability': args.boost,
            'support_help': support_help,
            'accumulate': args.accumulate,
        }, f)

    # train models
    red_model = ModelWrapper(shape, seed, epochs=epochs)
    blue_model = ModelWrapper(shape, seed, epochs=epochs)

    # support agents
    support_red = None
    support_blue = None

    if args.sar == 'greedy':
        support_red = GreedyAgent(RED, seed=seed)
    if args.sar == 'alphabeta':
        support_red = AlphaBetaAgent(RED, seed=seed)
    if args.sab == 'greedy':
        support_blue = GreedyAgent(BLUE, seed=seed)
    if args.sab == 'alphabeta':
        support_blue = AlphaBetaAgent(RED, seed=seed)

    # this is for continuous training
    if load_models:
        red_model.load_checkpoint(checkpoint, 'new_red.pth.tar')
        blue_model.load_checkpoint(checkpoint, 'new_blue.pth.tar')

    c = Coach(gen, red_model, blue_model, support_red, support_blue, boost, seed, max_weapon_per_figure, max_figure_per_scenario,
              max_move_no_response_size, max_attack_size, num_MCTS_sims, cpuct, max_depth, temp_threshold, parallel, checkpoint)
    t_red = Trainer(red_model, RED)
    t_blue = Trainer(blue_model, BLUE)

    history_red = []
    history_blue = []

    for it in range(num_iters):
        logger.info('Start training Iter #%s ...', it)

        if it > num_iters * support_help:
            c.support_enabled = False
            logger.info('support agents for training disabled')

        # collect episodes
        tr_red, tr_blue, tr_meta = c.generate(num_eps, it)

        # save meta information and training examples
        with open(os.path.join(checkpoint, 'episodes', f'checkpoint_{it}.json'), 'w') as f:
            json.dump(tr_meta, f, indent=4, sort_keys=True, default=str)
        with open(os.path.join(checkpoint, 'episodes', f'checkpoint_{it}_{RED}.examples.pkl'), 'wb') as f:
            pickle.dump(tr_red, f)
        with open(os.path.join(checkpoint, 'episodes', f'checkpoint_{it}_{BLUE}.examples.pkl'), 'wb') as f:
            pickle.dump(tr_blue, f)

        if args.accumulate:
            history_red += tr_red
            history_blue += tr_blue
            logging.info('accumulating %s new episodes for red and %s for blue', len(tr_red), len(tr_blue))
        else:
            history_red = tr_red
            history_blue = tr_blue

        if len(history_red) > max_tr_examples:
            history_red = history_red[-max_tr_examples:]
        if len(history_blue) > max_tr_examples:
            history_blue = history_blue[-max_tr_examples:]

        # train models
        t_red.train(tr_red, checkpoint, it)
        t_blue.train(tr_blue, checkpoint, it)

        # evaluate new models

        # TODO:

    logger.info('Starting the learning process')
