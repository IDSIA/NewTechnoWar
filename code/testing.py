# %%
from agents import MatchManager, GreedyAgent
from core.game.goals import GoalReachPoint, GoalDefendPoint, GoalMaxTurn
from core.const import RED, BLUE
from core.game import GameManager, GameBoard, GameState
from core.actions import *
from core.templates import buildFigure
from core.utils.coordinates import Hex
from utils.images import drawState, drawAction, drawHexagon
from PIL import Image
import utils.images
import numpy as np

from utils.setup_logging import setup_logging
setup_logging()

utils.images.SIZE = 32
utils.images.ALWAYS_TEXT = True

gm = GameManager()

# %%
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
)

state.addFigure(
    buildFigure('Infantry', (0, 0), RED, 'r_inf_1'),
    buildFigure('Infantry', (0, 4), BLUE, 'b_inf_1'),
)

drawState(board, state)

# %%

red = GreedyAgent(RED, seed=42)
blue = GreedyAgent(BLUE, seed=24)

mm = MatchManager('', red, blue, board, state, 2)
mm.play()

# %%

imgs = []

for s in mm.states_history:
    img = drawState(board, s, True)
    imgs.append(img)

imgs[0].save(
    'game5x5.gif',
    save_all=True,
    append_images=imgs[1:],
    optimize=False,
    loop=0,
    duration=500
)

# %%

shape = (11, 11)

board = GameBoard(shape)
state = GameState(shape)

goal = GoalReachPoint(RED, shape, [Hex(7, 1)])
board.addObjectives(goal)

terrain = np.zeros(shape, dtype='uint8')
terrain[5, 3:8] = 3
terrain[:, 6] = 1
board.addTerrain(terrain)

r1 = buildFigure('Tank', (3, 3), RED, 'r1')
r2 = buildFigure('Infantry', (6, 2), RED, 'r1')
b1 = buildFigure('Tank', (7, 7), BLUE, 'r1')
b2 = buildFigure('Infantry', (3, 7), BLUE, 'r1')

state.addFigure(r1, r2, b1, b2)

drawState(board, state)

# %% drawing actions for tank
img = drawState(board, state)

figure = r1

passes = gm.actionPassFigure(figure)
waits = gm.buildWaits(board, state, figure.team)
moves = gm.buildMovements(board, state, figure)
attacks = gm.buildAttacks(board, state, figure)
supports = gm.buildSupportAttacks(board, state, figure)

# %%

img = drawState(board, state)
for action in moves:
    drawHexagon(img, action.destination.tuple(), '#ff0000', 2, '#ff0000', 96)
    drawAction(img, action)

img

# %%

actions = []
remaining = []

min_neigh_sum = 2
top_n = 10

for move in moves:
    dst = move.destination
    neighbor = dst.range(1)
    neighbor_sum = sum(board.terrain[x.tuple()] for x in neighbor)
    if neighbor_sum > min_neigh_sum:
        actions.append(move)
    elif isinstance(move, MoveLoadInto):
        actions.append(move)
    else:
        remaining.append(move)

actions += sorted(remaining, key=lambda x: min([x.destination.distance(y) for y in board.getObjectiveMark()]))[:top_n]

img = drawState(board, state)
for action in actions:
    drawHexagon(img, action.destination.tuple(), '#ff0000', 2, '#ff0000', 96)
    drawAction(img, action)

print('saved ', len(actions) / len(moves), '%')

img

# %%
img = drawState(board, state)

for r in r1.position.range(3):
    drawHexagon(img, r.tuple(), 'red')

for r in r1.position.range(2):
    drawHexagon(img, r.tuple(), 'orange')

for r in r1.position.range(1):
    drawHexagon(img, r.tuple(), 'yellow')

img

# %%

r1.weapons['SG'].ammo = 1000

targets = r1.position.range(3)

imgs = []

for target in targets:
    state.smoke = np.zeros(shape)
    atg = gm.actionAttackGround(board, state, r1, target, r1.weapons['SG'])
    gm.step(board, state, atg)
    img = drawState(board, state, True)
    imgs.append(img)

# %%

imgs[0].save(
    'smoke.gif',
    save_all=True,
    append_images=imgs[1:],
    optimize=False,
    loop=0,
    duration=200
)
# %%
