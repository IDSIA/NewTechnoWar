"""
Testing game.
"""
import logging
import logging.config
import os

import numpy as np
import yaml

from core import TOTAL_TURNS, RED, BLUE
from core.actions import Shoot, Move, Action, ACTION_MOVE, ACTION_ATTACK
from core.game import GameManager
from core.game.scenarios import scenarioTest1v1, scenarioTest3v1, scenarioTestBench
from utils.drawing import draw_state, draw_show, fig2img, draw_hex_line

with open('logger.config.yaml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

DRAW_IMAGE = os.getenv("DRAW_IMAGE", False)

images = []


def draw_initial(gm):
    if DRAW_IMAGE:
        _, ax = draw_state(gm)
        im = draw_show(ax, title="Initial setup")
        images.append(fig2img(im))


def draw_round(gm: GameManager, action: Action, turn: int):
    if not DRAW_IMAGE:
        return
    fig, ax = draw_state(gm)
    if isinstance(action, Move):
        ax = draw_hex_line(ax, action.destination, color='green')
    if isinstance(action, Shoot):
        ax = draw_hex_line(ax, action.los, color='orange')
    im = draw_show(ax, title=f"Turn {turn}: {action}")
    images.append(fig2img(im))


def draw_save(gm):
    if DRAW_IMAGE:
        images[0].save(f"{gm.name}.gif", save_all=True, append_images=images[1:], optimize=False, duration=600,
                       loop=0)


def round(gm: GameManager, first: str, second: str, turn: int):
    figures = gm.activableFigures(first)
    if not figures:
        return

    # agent chooses figures
    f = np.random.choice(figures)

    moves = gm.buildMovements(first, f)
    shoots = gm.buildShoots(first, f)

    if not moves and not shoots:
        return

    whatDo = []

    if moves:
        whatDo.append(ACTION_MOVE)
    if shoots:
        whatDo.append(ACTION_ATTACK)

    # agent chooses type of action
    toa = np.random.choice(whatDo)

    actions = []

    if toa == ACTION_MOVE:
        actions = moves

    if toa == ACTION_ATTACK:
        actions = shoots

    action = np.random.choice(actions)
    draw_round(gm, action, turn)
    gm.activate(action)

    if isinstance(action, Shoot):
        responses = gm.buildResponses(second, action.target)

        if responses:
            if np.random.choice([True, False]):
                response = np.random.choice(responses)
                draw_round(gm, action, turn)
                gm.activate(response)


def play(gm: GameManager, seed=42):
    global images
    images = []
    np.random.seed(seed)

    logging.info(f'SCENARIO: {gm.name}')
    logging.info(f'SEED: {seed}')

    draw_initial(gm)

    for turn in range(TOTAL_TURNS):
        logging.info(f'Turn {turn + 1}')

        while gm.canActivate(RED) or gm.canActivate(BLUE):
            round(gm, RED, BLUE, turn)
            round(gm, BLUE, RED, turn)

        gm.update()

        if gm.goalAchieved():
            logging.info("End game!")
            break

    draw_save(gm)


if __name__ == "__main__":
    np.random.seed(42)

    gm1v1 = scenarioTest1v1()
    gm3v1 = scenarioTest3v1()
    gmTB = scenarioTestBench()

    play(gm1v1)
    play(gm3v1)
    play(gmTB)
