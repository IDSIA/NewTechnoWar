import logging
from os import replace
import numpy as np

from typing import Tuple

from core.utils.coordinates import Hex
from core.game import GameBoard, GameState, GoalReachPoint, GoalDefendPoint, GoalMaxTurn
from core.templates import buildFigure
from core.game.goals import GoalEliminateOpponent
from core.const import RED, BLUE

from utils.setup_logging import setup_logging
setup_logging()


logger = logging.getLogger(__name__)


def scenarioRandom5x5(seed: int = 0, scenario_seed: int = -1) -> Tuple[GameBoard, GameState]:

    seed_gen = np.random.default_rng(seed)

    l = 5
    shape = (l, l)

    generate_s = scenario_seed == -1

    while True:
        if generate_s:
            scenario_seed = seed_gen.integers(low=100000000, high=1000000000)
        logger.debug('random seed=%s s=%s', seed, scenario_seed)

        r = np.random.default_rng(scenario_seed)

        board = GameBoard(shape, gen_seed=scenario_seed)
        state = GameState(shape)

        terrain = np.zeros(shape, 'uint8')

        # trees
        n_trees = r.choice([0, 3, 5, 9], 1, p=[.4, .3, .2, .1])

        if n_trees > 0:
            xs = r.integers(low=0, high=l, size=n_trees)
            ys = r.integers(low=0, high=l, size=n_trees)

            for x, y in zip(xs, ys):
                terrain[x, y] = 2  # tree

        # buildings
        if r.random() > .3:
            for _ in range(r.integers(low=1, high=l)):
                x, y = r.integers(low=0, high=l, size=2)
                terrain[x, y] = 5

        # forests
        if r.random() > .4:
            for _ in range(r.integers(low=1, high=3)):
                x, y = r.integers(low=1, high=3, size=2)
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

        d = r.random()
        v = r.choice(l, 1)

        if d < .3:
            # road vertical
            terrain[v, :] = 1
        elif d < .6:
            # road horizontal
            terrain[:, v] = 1

        board.addTerrain(terrain)

        x, y = r.integers(low=1, high=l-1, size=2)
        max_turns = r.integers(low=5, high=12)

        goal = [Hex(x, y)]
        board.addObjectives(
            GoalReachPoint(RED, shape, goal),
            GoalDefendPoint(BLUE, RED, shape, goal),
            GoalMaxTurn(BLUE, max_turns),
            GoalEliminateOpponent(RED, BLUE),
            GoalEliminateOpponent(BLUE, RED),
        )

        pos_red_x = r.choice(range(0, l), 4)
        pos_red_y = r.choice(range(0, 2), 4)
        pos_blue_x = r.choice(range(0, l), 4)
        pos_blue_y = r.choice(range(l-2, l), 4)

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


def scenarioRandom10x10(seed: int = 0, scenario_seed: int = -1) -> Tuple[GameBoard, GameState]:
    seed_gen = np.random.default_rng(seed)

    shape = (10, 10)

    generate_s = scenario_seed == -1

    while True:
        if generate_s:
            scenario_seed = seed_gen.integers(low=100000000, high=1000000000)
        logger.debug('random seed=%s s=%s', seed, scenario_seed)

        r = np.random.default_rng(scenario_seed)

        board = GameBoard(shape, gen_seed=scenario_seed)
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
