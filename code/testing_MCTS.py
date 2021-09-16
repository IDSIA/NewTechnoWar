# %% imports and setup
import logging

import numpy as np

from agents import MatchManager, MCTSAgent
from core.const import RED, BLUE
from core.game import GameBoard, GameState, GoalReachPoint, GoalDefendPoint, GoalMaxTurn, GoalEliminateOpponent
from core.templates import buildFigure
from core.scenarios import scenarioRandom10x10, scenarioRandom5x5
from core.utils.coordinates import Hex

from utils.setup_logging import setup_logging

from utils.images import drawState

setup_logging()
logger = logging.getLogger("agents")

# %% random seed for repeatability
seed = 151775519

# %% scenario setup: this is a small dummy scenario for testing purposes
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

# %% agents setup

checkpoint = './temp.20210906.181122/'

agent_red = MCTSAgent(RED, board.shape, checkpoint, seed)
agent_blue = MCTSAgent(BLUE, board.shape, checkpoint, seed)

# %% setup match manager
mm = MatchManager('', agent_red, agent_blue, board, state, seed)

# %%
imgs = []
while not mm.end:
    mm.nextStep()
    img = drawState(mm.board, mm.state, True)
    imgs.append(img)

# %%

imgs[0].save(
    'mcts_10x10_1.gif',
    save_all=True,
    append_images=imgs[1:],
    optimize=False,
    loop=0,
    duration=200
)

# %% Random scenario generation

gen = scenarioRandom10x10(seed)

# %%

b, s = next(gen)
drawState(b, s)


# %%
mm = MatchManager('', agent_red, agent_blue, b, s, seed)
while not mm.end:
    mm.nextStep()
    img = drawState(mm.board, mm.state, True)

# %%
b, s = next(scenarioRandom10x10(s=408833426))
drawState(b, s)

# %%


def agent_mcts_1(team, seed):
    """This agent learned from always the same 10x10 board."""
    return MCTSAgent(team, (10, 10), './temp.20210903.151408', seed=seed)


def agent_mcts_2(team, seed):
    """This agent learned from always the same 10x10 board, standard parameters."""
    return MCTSAgent(team, (10, 10), './temp.20210901.160613', seed=seed)


def agent_mcts_rb(team, seed):
    """This agent learned from random 10x10 boards"""
    return MCTSAgent(team, (10, 10), './temp.20210903.172304', seed=seed)


def agent_mcts_rb_2(team, seed):
    """This agent learned from random 5x5 boards"""
    return MCTSAgent(team, (5, 5), './temp.20210906.150015', seed=seed)


def agent_mcts_rb_3(team, seed):
    """This agent learned from random 5x5 boards"""
    return MCTSAgent(team, (5, 5), './temp.20210906.153157', seed=seed)


def agent_mcts_rb_4(team, seed):
    """This agent learned from random 10x10 boards"""
    return MCTSAgent(team, (10, 10), './temp.20210906.181122', seed=seed)


# %%
seed = 4242424
scenario_seed = 123456789
scen_gen = scenarioRandom10x10(scenario_seed=scenario_seed)

# %%
red = agent_mcts_rb(RED, seed)
blue = agent_mcts_rb(BLUE, seed)
board, state = next(scen_gen)

mm = MatchManager('', red, blue, board, state, seed, True)

# %%
imgs = []
while not mm.end:
    mm.nextStep()
    img = drawState(mm.board, mm.state, True)
    imgs.append(img)

# %%

imgs[0].save(
    'mcts_trainedOnRandom_rb.gif',
    save_all=True,
    append_images=imgs[1:],
    optimize=False,
    loop=0,
    duration=200
)

# %%

gen = scenarioRandom5x5(1)

# %%
board, state = next(gen)
drawState(board, state)

# %%
