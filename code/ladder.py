import json
import logging
import os

import ray
from tqdm import tqdm

from agents import *
from core.const import RED, BLUE
from core.game import GameBoard, GameState
from core.scenarios.generators import scenarioRandom10x10

from utils.setup_logging import setup_logging

setup_logging()

logger = logging.getLogger(__name__)
os.environ['RAY_DISABLE_IMPORT_WARNING'] = '1'


@ray.remote
def play(seed, red_gen, blue_gen, board: GameBoard, state: GameState):
    p_red = red_gen.__name__
    p_blue = blue_gen.__name__

    logger.info('seed: %s red: %s blue: %s', seed, p_red, p_blue)

    red = red_gen(RED, seed)
    blue = blue_gen(BLUE, seed)

    try:
        mm = MatchManager('', red, blue, board, state, seed, False)

        t = tqdm(range(board.maxTurn), desc=f'R:{p_red:24} vs B:{p_blue:24}')
        while not mm.end:
            mm.nextStep()

            if (mm.state.turn > t.n):
                t.update(n=mm.state.turn)
        t.update(n=board.maxTurn)

    except Exception as e:
        logger.error('seed: %s red: %s blue: %s error: %s', seed, p_red, p_blue, str(e))
        logger.exception(e)
        return {
            'red': p_red,
            'blue': p_blue,
            'seed': seed,
            'winner': None,
            'error': str(e)
        }

    logger.info('seed: %s red: %s blue: %s winner: %s', seed, p_red, p_blue, mm.winner)
    return {
        'red': p_red,
        'blue': p_blue,
        'seed': seed,
        'winner': mm.winner,
    }


# -------------------------------------------------
# agents definitions
# -------------------------------------------------

def agent_random(team, seed):
    return RandomAgent(team, seed)


def agent_greedy(team, seed):
    return GreedyAgent(team, seed=seed)


def agent_ab(team, seed):
    return AlphaBetaAgent(team, seed=seed)


def agent_abf1(team, seed):
    return AlphaBetaFast1Agent(team, seed=seed)


def agent_mcts_1(team, seed):
    """This agent learned from always the same 10x10 board."""
    return MCTSAgent(team, (10, 10), './temp.20210903.151408', seed=seed)


def agent_mcts_2(team, seed):
    """This agent learned from always the same 10x10 board, standard parameters."""
    return MCTSAgent(team, (10, 10), './temp.20210901.160613', seed=seed)


def agent_mcts_rb(team, seed):
    """This agent learned from random 10x10 boards"""
    return MCTSAgent(team, (10, 10), './temp.20210903.172304', seed=seed)


agents = [
    agent_random,
    agent_greedy,
    agent_ab,
    agent_abf1,
    agent_mcts_1,
    agent_mcts_2,
    agent_mcts_rb,
]


if __name__ == '__main__':
    ray.init()

    seed = 4242424
    scenario_seed = 123456789
    num_games = 1  # 10

    scen_gen = scenarioRandom10x10(scenario_seed=123456789)

    # play games
    tasks = []
    for i in range(num_games):
        for red_gen in agents:
            for blue_gen in agents:
                board, state = next(scen_gen)
                tasks.append(play.remote(seed, red_gen, blue_gen, board, state))

    logger.info('started %s games', len(tasks))

    # collect results
    results = []
    for task in tasks:
        results.append(ray.get(task))

    with open('ladder_results.json', 'w+') as f:
        json.dump(results, f)
