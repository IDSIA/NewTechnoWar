# %%
import pandas as pd
import os
import pickle

import matplotlib.pyplot as plt

from PIL.Image import frombytes
from agents import GreedyAgent, MatchManager
from agents.reinforced import MCTSAgent
from core.const import RED, BLUE
from core.scenarios.generators import scenarioRandom5x5, scenarioRandom10x10
from utils.images import drawState

# %%
# DIR_MODELS = './temp.20210918.142304/models/'
DIR_MODELS = './temp.20210918.125422/models/'
SEED = 0

# SHAPE = (5,5)
SHAPE = (10, 10)

reds = [GreedyAgent(RED, True, SEED)]
blues = [GreedyAgent(BLUE, True, SEED)]

file_metrics_red = []
file_metrics_blue = []

dirs = []
for item in os.listdir(DIR_MODELS):
    dir_model = os.path.join(DIR_MODELS, item)
    if os.path.isdir(dir_model) and len(os.listdir(dir_model)) == 4:
        dirs.append(dir_model)

for d in sorted(dirs):
    print(d)
    item = d.split('/')[-1]
    reds.append(MCTSAgent(RED, SHAPE, d, SEED, name=f'MCTS-{item}'))
    blues.append(MCTSAgent(BLUE, SHAPE, d, SEED, name=f'MCTS-{item}'))
    file_metrics_red.append(os.path.join(d, f'checkpoint_metrics_{item}_red.tsv'))
    file_metrics_blue.append(os.path.join(d, f'checkpoint_metrics_{item}_blue.tsv'))

scenario_seed = 489346562
# scen_gen = scenarioRandom5x5(scenario_seed=scenario_seed)
scen_gen = scenarioRandom10x10(scenario_seed=scenario_seed)

# %%

all_imgs = []
max_frames = 0

for red in reds:
    for blue in blues:
        board, state = next(scen_gen)

        mm = MatchManager('', red, blue, board, state, SEED, True)

        imgs = []
        while not mm.end:
            try:
                mm.nextStep()
                img = drawState(mm.board, mm.state, True)
                imgs.append(img)
            except Exception as _:
                break

        max_frames = max(max_frames, len(imgs))
        all_imgs.append((red.name, blue.name, imgs))

with open('animations.pkl', 'wb+') as f:
    pickle.dump((max_frames, all_imgs), f)

# %%

with open('animations.pkl', 'rb+') as f:
    max_frames, all_imgs = pickle.load(f)

# %%
n_r = len(reds)
n_b = len(blues)
f, ax = plt.subplots(n_r, n_b, figsize=(14, 14))

frames = []

for j in range(max_frames):
    for r in range(n_r):
        for b in range(n_b):
            i = r * n_b + b
            r_name, b_name, images = all_imgs[i]
            if r == 0:
                ax[r, b].set_title(f'b: {b_name}')
            if b == 0:
                ax[r, b].set_ylabel(f'r: {r_name}')

            if j < len(images):
                ax[r, b].imshow(images[j])

    f.canvas.draw()
    frames.append(frombytes('RGB', f.canvas.get_width_height(), f.canvas.tostring_rgb()))

# %%

frames[0].save(
    'validation.gif',
    save_all=True,
    append_images=frames[1:],
    optimize=False,
    loop=0,
    duration=500
)

# %%
dfs_red, dfs_blue = [], []

for mr, mb in zip(file_metrics_red, file_metrics_blue):
    dfs_red.append(pd.read_csv(mr, sep='\t'))
    dfs_blue.append(pd.read_csv(mb, sep='\t'))

# %%
