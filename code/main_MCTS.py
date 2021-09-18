import logging

import argparse
import os
import pickle
import json

from datetime import datetime
from typing import Tuple

import numpy as np
import ray
import torch

from tqdm import tqdm
from ray.exceptions import GetTimeoutError

from core.const import RED, BLUE
from core.scenarios.generators import scenarioRandom10x10, scenarioRandom5x5
from core.templates import buildFigure
from core.game import GameBoard, GameState, GoalReachPoint, GoalDefendPoint, GoalMaxTurn, GoalEliminateOpponent
from core.utils.coordinates import Hex

from agents.reinforced import ModelWrapper, Episode

from utils.setup_logging import setup_logging
setup_logging()

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

    # number of workers to use
    NUM_CORES: int = max(1, os.environ.get('NUM_CORES', os.cpu_count() - 1))
    # GPU to use
    NUM_GPUS: int = os.environ.get('NUM_GPUS', torch.cuda.device_count())
    GPU: int = 0
    TIMEOUT: int = 240

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

    # game parameters: TODO: derive by game files
    max_weapon_per_figure: int = 8
    max_figure_per_scenario: int = 6
    max_move_no_response_size: int = 1351
    max_attack_size: int = 288

    # unknown parameters...
    cpuct: int = 1
    temp_threshold: int = 15

    p = argparse.ArgumentParser()
    # resources
    p.add_argument('-c', '--cpus', type=int, default=NUM_CORES, help=f'default: {NUM_CORES}\tnumber of cores to use (worker)')
    p.add_argument('-g', '--gpu', type=int, default=GPU, help=f'default: {GPU}\tGPU id to use (from 0 to {NUM_GPUS-1})')
    p.add_argument('-s', '--seed', type=int, default=SEED, help=f'default: {SEED}\trandom seed to use')
    p.add_argument('-t', '--timeout', type=int, default=TIMEOUT, help=f'default: {TIMEOUT}\tset timeout for episode generation in seconds')
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
    p.add_argument('-sh', '--support-help', type=float, default=SUPPORT_HELP, dest='shelp',
                   help=f'default: {SUPPORT_HELP}\tpercentage of iterations with help (starting from first)')
    p.add_argument('-b', '--support-boost', type=float, default=SUPPORT_BOOST_PROB, dest='boost',
                   help=f'default: {SUPPORT_BOOST_PROB}\tboost probability for support chosen actions')
    args = p.parse_args()

    device: str = 'cpu'
    if torch.cuda.is_available():
        device: str = f'cuda:{args.gpu}'

    logger.info("Using %s workers", args.cpus)
    logger.info("Using device %s for training", device)

    # if true,use ray and parallel execution of episodes
    parallel = args.cpus > 1
    if parallel:
        # ray.init(num_cpus=args.cpus, num_gpus=args.gpus)
        ray.init(num_cpus=args.cpus)

    # random seed for repeatability
    seed = args.seed
    timeout = args.timeout

    # this is a small dummy scenario for testing purposes
    game_generator = None
    shape = None
    if args.s5:
        game_generator = scenario5x5()
        shape = (5, 5)
    if args.r5:
        game_generator = scenarioRandom5x5(seed)
        shape = (5, 5)
    if args.s10:
        game_generator = scenario10x10()
        shape = (10, 10)
    if args.r10:
        game_generator = scenarioRandom10x10(seed)
        shape = (10, 10)

    if not game_generator:
        logger.error("no scenario selected")
        exit(1)

    # training arguments setup
    epochs = args.epochs
    num_iters = args.iters
    num_eps = args.episodes
    max_tr_examples = args.qlen
    num_MCTS_sims = args.sims
    load_models = args.load
    boost = args.boost
    max_depth = args.depth

    support_red = args.sar
    support_blue = args.sab
    support_help = args.shelp
    support_boost = args.boost

    DIR_CHECKPOINT = args.dir
    DIR_MODELS = os.path.join(DIR_CHECKPOINT, 'models')
    DIR_EPISODES = os.path.join(DIR_CHECKPOINT, 'episodes')

    os.makedirs(DIR_MODELS, exist_ok=True)
    os.makedirs(DIR_EPISODES, exist_ok=True)

    with open(os.path.join(DIR_CHECKPOINT, f'config.{NOW}.json'), 'w') as f:
        json.dump({
            'start': NOW,
            '5x5': args.s5,
            '10x10': args.s10,
            'random5x5': args.r5,
            'random10x10': args.r10,
            'cpus': args.cpus,
            'gpus': args.gpu,
            'device': device,
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
            'checkpoint': DIR_CHECKPOINT,
            'support_red': support_red,
            'support_blue': support_blue,
            'boost_probability': support_boost,
            'support_help': support_help,
            'accumulate': args.accumulate,
        }, f)

    # workers definition:

    workers = [Episode.remote(
        DIR_CHECKPOINT, support_red, support_blue, support_boost, max_weapon_per_figure, max_figure_per_scenario,
        max_move_no_response_size, max_attack_size, num_MCTS_sims, max_depth, cpuct
    ) for _ in range(args.cpus)]

    train_examples = {
        RED: [],
        BLUE: []
    }

    for it in range(num_iters):
        logger.info('Start Iter #%s ...', it)

        DIR_IT = os.path.join(DIR_MODELS, str(it))
        os.makedirs(DIR_IT)

        support_enabled = it < num_iters * support_help
        logger.info('support agents for training %s', 'enabled' if support_enabled else 'disabled')

        logger.info('start self-play iter #%s', it)

        # collect episodes
        tasks, tr_red, tr_blue, tr_meta = [], [], [], []
        i = 0
        while i < num_eps:
            for w in workers:
                board, state = next(game_generator)
                tasks.append(w.execute.remote(board, state, seed+i, temp_threshold, it > 0, support_enabled))
                i += 1
                if i >= num_eps:
                    break

        task_timed_out = 0
        task_failed = 0
        t = tqdm(tasks, desc="Self Play")
        for task in t:
            try:
                tr_ex_red, tr_ex_blue, tr_ex_meta = ray.get(task, timeout=timeout)
                tr_red += tr_ex_red
                tr_blue += tr_ex_blue
                tr_meta += tr_ex_meta

                if not tr_ex_meta['completed']:
                    task_failed += 1

            except GetTimeoutError as _:
                task_timed_out += 1

            t.set_postfix(Timedout=f'{task_timed_out:3}', Failed=f'{task_failed:3}', tr_blue=len(tr_blue), tr_red=len(tr_red))
            t.update()

        # save meta information and training examples
        with open(os.path.join(DIR_EPISODES, f'checkpoint_{it}_meta.json'), 'w') as f:
            json.dump(tr_meta, f, indent=4, sort_keys=True, default=str)
        with open(os.path.join(DIR_EPISODES, f'checkpoint_{it}_{RED}_examples.pkl'), 'wb') as f:
            pickle.dump(tr_red, f)
        with open(os.path.join(DIR_EPISODES, f'checkpoint_{it}_{BLUE}_examples.pkl'), 'wb') as f:
            pickle.dump(tr_blue, f)

        logger.info('end self-play iter #%s', it)

        if args.accumulate:
            train_examples[RED] += tr_red
            train_examples[BLUE] += tr_blue
            logging.info('accumulating %s new episodes for red and %s for blue', len(tr_red), len(tr_blue))
        else:
            train_examples[RED] = tr_red
            train_examples[BLUE] = tr_blue

        if len(train_examples[RED]) > max_tr_examples:
            train_examples[RED] = train_examples[RED][-max_tr_examples:]
        if len(train_examples[BLUE]) > max_tr_examples:
            train_examples[BLUE] = train_examples[BLUE][-max_tr_examples:]

        # train models
        for team in [RED, BLUE]:
            tr_examples = train_examples[team]

            n_ex = len(tr_examples)
            p_win = sum(1 for e in tr_examples if e[2] > 0)/n_ex

            logger.info('using %s examples (wins: %s) for training %s model', n_ex, p_win, team)

            model = ModelWrapper(shape, seed, epochs, device=device, max_move_no_response_size=max_move_no_response_size, max_attack_size=max_attack_size)
            model.train(tr_examples, team)

            # save new model
            model.save_checkpoint(folder=DIR_IT, filename=f'model_{team}.pth.tar')
            model.save_checkpoint(folder=DIR_CHECKPOINT, filename=f'model_{team}.pth.tar')

            # save metrics history
            filename = os.path.join(DIR_IT, f'checkpoint_metrics_{it}_{team}.tsv')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\t'.join(['i', 'l_pi', 'l_v']))
                f.write('\n')
                for x in range(len(model.history)):
                    l_pi, l_v = model.history[x]
                    f.write('\t'.join([str(a) for a in [x, l_pi, l_v]]))
                    f.write('\n')

        # evaluate new models

        # TODO:

    logger.info('Starting the learning process')
