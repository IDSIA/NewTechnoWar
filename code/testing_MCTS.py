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
from utils import dotdict

from utils.setup_logging import setup_logging

from utils.images import drawState

setup_logging()
logger = logging.getLogger(__name__)

# %% random seed for repeatability
seed = 151775519

# %% scenario setup: this is a small dummy scenario for testing purposes
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
    GoalEliminateOpponent(RED, BLUE),
    GoalEliminateOpponent(BLUE, RED),
    GoalMaxTurn(BLUE, 6),
)

state.addFigure(
    buildFigure('Infantry', (0, 0), RED, 'r_inf_1'),
    buildFigure('Infantry', (0, 4), BLUE, 'b_inf_1'),
)

# %% agents setup

args = dotdict({
    'numMCTSSims': 30,
    'cpuct': 1,
    'checkpoint': './temp.20210827.194547/',
    'maxMoveNoResponseSize': 1351,
    'maxAttackSize': 288,
    'maxWeaponPerFigure': 8,
    'maxFigurePerScenario': 6,
    'seed': seed,
})

agent_red = MCTSAgent(RED, board, args)
agent_blue = MCTSAgent(BLUE, board, args)

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
