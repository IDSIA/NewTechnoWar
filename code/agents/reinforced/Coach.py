import logging

import numpy as np
import ray

from tqdm import tqdm

from agents import Agent
from agents.reinforced.Episode import Episode
from agents.reinforced.nn import ModelWrapper

from core.const import RED, BLUE

logger = logging.getLogger(__name__)


class Coach():
    """
    This class executes the self-play. It uses the functions defined in Game and NeuralNet.
    """

    def __init__(self,
                 game_generator,
                 red_model: ModelWrapper,
                 blue_model: ModelWrapper,
                 support_red: Agent or None = None,
                 support_blue: Agent or None = None,
                 support_boast_prob: float = 1.0,
                 seed: int = 0,
                 max_weapon_per_figure: int = 8,
                 max_figure_per_scenario: int = 6,
                 max_move_no_response_size: int = 1351,
                 max_attack_size: int = 288,
                 num_MCTS_sims: int = 30,
                 cpuct: int = 1,
                 max_depth: int = 100,
                 temp_threshold: int = 15,
                 parallel: bool = True,
                 folder_checkpoint: str = '.',
                 ):
        self.seed: int = seed
        self.random = np.random.default_rng(self.seed)

        self.game_generator = game_generator

        self.parallel: bool = parallel

        self.folder_ceckpoint: str = folder_checkpoint

        self.max_weapon_per_figure: int = max_weapon_per_figure
        self.max_figure_per_scenario: int = max_figure_per_scenario
        self.max_move_no_response_size: int = max_move_no_response_size
        self.max_attack_size: int = max_attack_size
        self.num_MCTS_sims: int = num_MCTS_sims
        self.cpuct: int = cpuct
        self.max_depth = max_depth
        self.temp_threshold: int = temp_threshold

        self.red: ModelWrapper = red_model
        self.blue: ModelWrapper = blue_model

        self.support_red: Agent or None = support_red
        self.support_blue: Agent or None = support_blue
        self.support_boast_prob: float = support_boast_prob
        self.support_enabled: bool = True

    def generate(self, num_eps: int, it: int):
        tr_examples_red = []
        tr_examples_blue = []
        tr_meta = []

        logger.info('Sart Self Play Iter #%s', it)

        support_red, support_blue = None, None
        if self.support_enabled:
            support_red = self.support_red
            support_blue = self.support_blue

        if self.parallel:
            episodes = [Episode.remote(
                self.red, self.blue, support_red, support_blue, self.support_boast_prob, self.seed + c, self.max_weapon_per_figure,
                self.max_figure_per_scenario, self.max_move_no_response_size, self.max_attack_size, self.num_MCTS_sims, self.cpuct, self.max_depth
            ) for c in range(num_eps)]

            # this uses ray's parallelism
            tasks = []

            for c, episode in enumerate(episodes):
                board, state = next(self.game_generator)
                task = episode.execute.remote(board, state, self.seed + c + it, self.temp_threshold)
                tasks.append(task)

            for task in tqdm(tasks, desc="Self Play"):
                episode: Episode = ray.get(task)

                tr_meta.append(episode.meta())
                tr_examples_red += (episode.examples[RED])
                tr_examples_blue += (episode.examples[BLUE])

        else:
            # this uses single thread
            episodes = [Episode(
                self.red, self.blue, self.support_red, self.support_blue, self.support_boast_prob, self.seed + c, self.max_weapon_per_figure,
                self.max_figure_per_scenario, self.max_move_no_response_size, self.max_attack_size, self.num_MCTS_sims, self.cpuct, self.max_depth
            ) for c in range(num_eps)]

            for c, episode in enumerate(episodes):
                board, state = next(self.game_generator)
                episode.execute(board, state, self.seed + c + it, self.temp_threshold)

                tr_meta.append(episode.meta)
                tr_examples_red += episode.examples[RED]
                tr_examples_blue += episode.examples[BLUE]

        logger.info('End Self Play Iter #%s', it)

        return tr_examples_red, tr_examples_blue, tr_meta
