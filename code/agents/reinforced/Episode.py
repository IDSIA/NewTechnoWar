import logging
from typing import Any, Dict
from datetime import datetime, timedelta

import numpy as np
import ray

from agents import Agent, Puppet, MatchManager
from agents.reinforced.MCTS import MCTS
from agents.reinforced.nn.Wrapper import ModelWrapper
from agents.reinforced.utils import ACT, RES

from core.const import BLUE, RED
from core.game.board import GameBoard
from core.game.state import GameState

from utils.copy import deepcopy

logger = logging.getLogger(__name__)


@ray.remote
class Episode:

    seed: int
    scenario_seed: int
    completed: bool

    start_time: datetime
    end_time: datetime
    duration: timedelta

    winner: str or None
    steps: int

    mcts: MCTS
    examples: Dict[str, list]

    support: Dict[str, Agent or None]
    support_boost_prob: float

    def __init__(self,
                 model_red: ModelWrapper,
                 model_blue: ModelWrapper,
                 support_red: Agent = None,
                 support_blue: Agent = None,
                 support_boost_prob: float = 1.0,
                 seed: int = 0,
                 max_weapon_per_figure: int = 8,
                 max_figure_per_scenario: int = 6,
                 max_move_no_response_size: int = 1351,
                 max_attack_size: int = 288,
                 num_MCTS_sims: int = 30,
                 cpuct: float = 1,
                 max_depth: int = 100,
                 ) -> None:

        self.seed = seed

        self.winner = None
        self.steps = 0

        self.support = {
            RED: support_red,
            BLUE: support_blue,
        }

        self.support_boost_prob = support_boost_prob

        self.mcts = MCTS(model_red, model_blue, seed, max_weapon_per_figure, max_figure_per_scenario, max_move_no_response_size, max_attack_size, num_MCTS_sims, cpuct, max_depth)
        self.examples = {
            RED: [],
            BLUE: [],
        }

    def meta(self) -> Dict[str, Any]:
        return {
            'seed': self.seed,
            'scenario_seed': self.scenario_seed,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'winner': self.winner,
            'steps': self.steps,
            'completed': self.completed,
            'num_episodes_red': len(self.examples[RED]),
            'num_episodes_blue': len(self.examples[BLUE]),
        }

    def execute(self, board: GameBoard, state: GameState, seed: int = 0, temp_threshold: int = 1):
        """
        This function executes one episode of self-play, starting with RED player.
        As the game is played, each turn is added as a training example to
        trainExamples. The game is played till the game ends. After the game
        ends, the outcome of the game is used to assign values to each example
        in trainExamples.

        It uses a temp=1 if episodeStep < tempThreshold, and thereafter
        uses temp=0.

        Returns:
            trainExamples: a list of examples of the form (board, current player, pi, v)
                            pi is the MCTS informed policy vector, v is +1 if
                            the player eventually won the game, else -1.
        """
        self.scenario_seed = seed
        self.completed = False

        train_examples: Dict[str, list] = {
            RED: [],
            BLUE: [],
        }

        # puppets agents are used to train a MTCS both for RED and BLUE point of view
        puppet: Dict[str, Puppet] = {
            RED: Puppet(RED),
            BLUE: Puppet(BLUE),
        }

        random: np.random.Generator = np.random.default_rng(seed)

        mm: MatchManager = MatchManager('', puppet[RED], puppet[BLUE], board, deepcopy(state), seed, False)

        self.steps: int = 0
        self.start_time = datetime.now()

        try:
            while not mm.end:
                self.steps += 1

                temp = int(self.steps < temp_threshold)

                board = mm.board
                state = deepcopy(mm.state)
                action_type, team, _ = mm.nextPlayer()

                logger.debug(f'Episode step: {self.steps} action: {action_type}')

                if action_type in ('update', 'init', 'end'):
                    mm.nextStep()
                    continue

                action_type = ACT if action_type == 'round' else RES

                logger.debug('Condition from coach BEFORE call getActionProb %s', state)

                _, valid_actions = self.mcts.actionIndexMapping(board, state, team, action_type)

                features: np.ndarray = self. mcts.generateFeatures(board, state)

                pi, _ = self. mcts.getActionProb(board, state, team, action_type, temp=temp)

                # change the probabilities pi based on action choosed by support agent (if given)
                if self.support[team]:
                    agent = self.support[team]
                    if action_type == ACT:
                        action = agent.chooseAction(board, state)
                    else:
                        action = agent.chooseResponse(board, state)

                    for i, va in enumerate(valid_actions):
                        if str(va) == str(action):
                            pi[i] += self.support_boost_prob
                            pi = pi/pi.sum()
                            break

                example = [features, pi]

                train_examples[team].append(example)

                if max(pi) == 1:
                    action_index = np.argmax(pi)
                    logger.debug(f'Unexpected single choice! Index: {action_index}')
                else:
                    action_index = random.choice(len(pi), p=pi)

                # choose next action and load in correct puppet
                action = valid_actions[action_index]

                # assuming action/response are selected correctly
                puppet[team].action = action
                puppet[team].response = action

                mm.nextStep()

            self.winner = mm.winner

            self.end_time = datetime.now()
            self.duration = self.end_time - self.start_time

            logger.debug('elapsed time: %s', self.duration)

            # assign victory: 1 is winner, -1 is loser
            r, b = (1, -1) if self.winner == RED else (-1, 1)

            # board, team, pi, winner
            self.examples[RED] = [(features, pi, r) for features, pi in train_examples[RED]]
            self.examples[BLUE] = [(features, pi, b) for features, pi in train_examples[BLUE]]

            self.completed = True

        except Exception as e:
            # clear
            logger.error(f'Episode failed: {e}')
            logger.exception(e)

            self.examples[RED] = []
            self.examples[BLUE] = []

        return self
