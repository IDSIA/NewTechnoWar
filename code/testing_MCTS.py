# %% imports and setup
import logging

import numpy as np

from agents.reinforced.MCTSAgent import MCTSAgent
from agents import MatchManager
from core.const import RED, BLUE
from core.game import GameBoard, GameState, GoalReachPoint, GoalDefendPoint, GoalMaxTurn
from core.game.goals import GoalEliminateOpponent
from core.templates import buildFigure
from core.utils.coordinates import Hex

from utils.setup_logging import setup_logging

from utils.images import drawState

setup_logging()
logger = logging.getLogger(__name__)

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

checkpoint = './temp.20210903.081951/'

agent_red = MCTSAgent(RED, board, checkpoint, seed)
agent_blue = MCTSAgent(BLUE, board, checkpoint, seed)

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
    'mcts_5x5.gif',
    save_all=True,
    append_images=imgs[1:],
    optimize=False,
    loop=0,
    duration=200
)

# %%
