# %% imports and setup
import logging
from typing import Tuple

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

checkpoint = './temp.20210903.151408/'

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

# %% Random scenario generation


def scenarioRandom10x10(seed: int = 0, s: int = -1) -> Tuple[GameBoard, GameState]:
    seed_gen = np.random.default_rng(seed)

    shape = (10, 10)

    generate_s = s == -1

    while True:
        if generate_s:
            s = seed_gen.integers(low=100000000, high=1000000000)
        logger.info('random seed=%s s=%s', seed, s)

        r = np.random.default_rng(s)

        board = GameBoard(shape)
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
