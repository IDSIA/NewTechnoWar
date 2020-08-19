"""
Testing game.
"""
import logging
import logging.config
import os

import numpy as np
import yaml

from core import TOTAL_TURNS, RED, BLUE
from core.actions import Attack, Move, Action
from core.game.board import GameBoard
from core.game.manager import GameManager
from core.game.state import GameState
from scenarios import scenarioTest1v1, scenarioTest3v1, scenarioTestBench, scenarioTest2v2
from utils.drawing import draw_state, draw_show, fig2img, draw_hex_line

dir_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dir_path, 'logger.config.yaml'), 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)

DRAW_IMAGE = os.getenv("DRAW_IMAGE", False)

ACTION_MOVE = 0
ACTION_ATTACK = 1

images = []


def draw_initial(board: GameBoard, state: GameState):
    if DRAW_IMAGE:
        _, ax = draw_state(board, state)
        im = draw_show(ax, title="Initial setup")
        images.append(fig2img(im))


def draw_round(board: GameBoard, state: GameState, action: Action, turn: int):
    if not DRAW_IMAGE:
        return
    fig, ax = draw_state(board, state)
    if isinstance(action, Move):
        ax = draw_hex_line(ax, action.destination, color='green')
    if isinstance(action, Attack):
        ax = draw_hex_line(ax, action.los, color='orange')
    im = draw_show(ax, title=f"Turn {turn}: {action}")
    images.append(fig2img(im))


def draw_save(gm):
    if DRAW_IMAGE:
        images[0].save(f"{gm.name}.gif", save_all=True, append_images=images[1:], optimize=False, duration=600, loop=0)


def round(gm: GameManager, board: GameBoard, state: GameState, first: str, turn: int):
    figures = state.getFiguresCanBeActivated(first)
    if not figures:
        return

    # agent chooses figures
    f = np.random.choice(figures)

    moves = gm.buildMovements(board, state, f)
    shoots = gm.buildAttacks(board, state, f)

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
    draw_round(board, state, action, turn)
    gm.step(board, state, action)

    if isinstance(action, Attack):
        target = state.getTarget(action)
        responses = gm.buildResponses(board, state, target)

        if responses:
            if np.random.choice([True, False]):
                response = np.random.choice(responses)
                draw_round(board, state, action, turn)
                gm.step(board, state, response)


def play(scene, seed=42):
    global images
    images = []
    np.random.seed(seed)

    board, state = scene
    gm: GameManager = GameManager()

    logging.info(f'SCENARIO: {board.name}')
    logging.info(f'SEED: {seed}')

    gm.update(state)

    draw_initial(board, state)

    for turn in range(TOTAL_TURNS):
        logging.info(f'Turn {turn + 1}')

        while state.getFiguresCanBeActivated(RED) or state.getFiguresCanBeActivated(BLUE):
            round(gm, board, state, RED, turn)
            round(gm, board, state, BLUE, turn)

        gm.update(state)

        if gm.goalAchieved(board, state):
            logging.info("End game!")
            break

    draw_save(gm)


if __name__ == "__main__":
    np.random.seed(42)

    gm1v1 = scenarioTest1v1()
    gm2v2 = scenarioTest2v2()
    gm3v1 = scenarioTest3v1()
    gmTB = scenarioTestBench()

    play(gm1v1)
    play(gm2v2)
    play(gm3v1)
    play(gmTB)
