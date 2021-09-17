import logging
from typing import Dict
from datetime import datetime

import numpy as np
import ray

from agents import Puppet, MatchManager, AlphaBetaAgent, GreedyAgent
from agents.reinforced.MCTS import MCTS
from agents.reinforced.nn.Wrapper import ModelWrapper
from agents.reinforced.utils import ACT, RES

from core.const import BLUE, RED
from core.game import GameBoard, GameState

from utils.copy import deepcopy

logger = logging.getLogger(__name__)


@ray.remote
class Episode:

    def __init__(self,
                 checkpoint: str = '.',
                 support_red: str = None,
                 support_blue: str = None,
                 support_boost_prob: float = 1.0,
                 max_weapon_per_figure: int = 8,
                 max_figure_per_scenario: int = 6,
                 max_move_no_response_size: int = 1351,
                 max_attack_size: int = 288,
                 num_MCTS_sims: int = 30,
                 max_depth: int = 100,
                 cpuct: float = 1,
                 ) -> None:

        self.support = {
            RED: support_red,
            BLUE: support_blue,
        }

        self.checkpoint = checkpoint
        self.support_boost_prob = support_boost_prob
        self.max_weapon_per_figure = max_weapon_per_figure
        self.max_figure_per_scenario = max_figure_per_scenario
        self.max_move_no_response_size = max_move_no_response_size
        self.max_attack_size = max_attack_size
        self.num_MCTS_sims = num_MCTS_sims
        self.cpuct = cpuct
        self.max_depth = max_depth

    def get_support(self, team, seed, enabled):
        if not enabled:
            return None
        if self.support[team] == 'greedy':
            return GreedyAgent(team, seed=seed)
        if self.support[team] == 'alphabeta':
            return AlphaBetaAgent(team, seed=seed)
        return None

    def execute(self, board: GameBoard, state: GameState, seed: int = 0, temp_threshold: int = 1, load_models: bool = True, support_enabled: bool = True):
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

        completed = False

        # train examples generated
        examples: Dict[str, list] = {
            RED: [],
            BLUE: [],
        }

        # setup models
        red = ModelWrapper(board.shape, seed)
        blue = ModelWrapper(board.shape, seed)

        if load_models:
            red.load_checkpoint(self.checkpoint, 'model_red.pth.tar')
            blue.load_checkpoint(self.checkpoint, 'model_blue.pth.tar')

        # setup MCTS
        mcts = MCTS(red, blue, seed, self.max_weapon_per_figure, self.max_figure_per_scenario,
                    self.max_move_no_response_size, self.max_attack_size, self.num_MCTS_sims, self.cpuct, self.max_depth)

        support = {
            RED: self.get_support(RED, seed, support_enabled),
            BLUE: self.get_support(BLUE, seed, support_enabled),
        }

        # puppets agents are used to train a MTCS both for RED and BLUE point of view
        puppet: Dict[str, Puppet] = {
            RED: Puppet(RED),
            BLUE: Puppet(BLUE),
        }

        random: np.random.Generator = np.random.default_rng(seed)

        mm: MatchManager = MatchManager('', puppet[RED], puppet[BLUE], board, deepcopy(state), seed, False)

        steps: int = 0
        start_time = datetime.now()
        winner: str = None

        try:
            while not mm.end:
                steps += 1

                temp = int(steps < temp_threshold)

                board = mm.board
                state = deepcopy(mm.state)
                action_type, team, _ = mm.nextPlayer()

                logger.debug(f'Episode step: {steps} action: {action_type}')

                if action_type in ('update', 'init', 'end'):
                    mm.nextStep()
                    continue

                action_type = ACT if action_type == 'round' else RES

                logger.debug('Condition from coach BEFORE call getActionProb %s', state)

                valid_indices, valid_actions = mcts.actionIndexMapping(board, state, team, action_type)
                actions = valid_actions[valid_indices]

                features = mcts.generateFeatures(board, state)

                pi, _ = mcts.getActionProb(board, state, team, action_type, temp=temp)

                # change the probabilities pi based on action choosed by support agent (if given)
                if support[team]:
                    agent = support[team]
                    if action_type == ACT:
                        action = agent.chooseAction(board, state)
                    else:
                        action = agent.chooseResponse(board, state)

                    for i, va in enumerate(valid_actions):
                        if va and str(va) == str(action):
                            pi[i] += self.support_boost_prob
                            pi /= pi.sum()
                            break

                example = [features, pi]

                examples[team].append(example)

                pi: np.ndarray = pi[valid_indices]
                pi_sum = pi.sum()
                if pi_sum > 0:
                    pi /= pi.sum()
                else:
                    logger.warn(f'Unexpected no probability vector!')
                    pi = np.ones(pi.shape)
                    pi /= pi.sum()

                if max(pi) == 1:
                    logger.debug(f'Unexpected single choice! Index: {np.argmax(pi)}')

                # choose next action and load in correct puppet
                action = random.choice(actions, p=pi)

                # assuming action/response are selected correctly
                puppet[team].action = action
                puppet[team].response = action

                mm.nextStep()

            winner = mm.winner

            # assign victory: 1 is winner, -1 is loser
            r, b = (1, -1) if winner == RED else (-1, 1)

            # board, team, pi, winner
            examples[RED] = [(features, pi, r) for features, pi in examples[RED]]
            examples[BLUE] = [(features, pi, b) for features, pi in examples[BLUE]]

            completed = True

        except Exception as e:
            # clear
            logger.error(f'Episode failed, reason: {e}')
            logger.exception(e)

            examples[RED] = []
            examples[BLUE] = []

        end_time = datetime.now()
        duration = end_time - start_time

        logger.debug('elapsed time: %s', duration)

        meta = {
            'support_boost_prob': self.support_boost_prob,
            'max_weapon_per_figure': self.max_weapon_per_figure,
            'max_figure_per_scenario': self.max_figure_per_scenario,
            'max_move_no_response_size': self.max_move_no_response_size,
            'max_attack_size': self.max_attack_size,
            'num_MCTS_sims': self.num_MCTS_sims,
            'cpuct': self.cpuct,
            'max_depth': self.max_depth,
            'temp_threshold': temp_threshold,
            'seed': seed,
            'scenario_seed': board.gen_seed,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'winner': winner,
            'steps': steps,
            'completed': completed,
            'num_episodes_red': len(examples[RED]),
            'num_episodes_blue': len(examples[BLUE]),
            'support_enabled': support_enabled,
            'support_red': support[RED],
            'support_blue': support[BLUE],
        }

        if not completed:
            logger.error('meta data of failed episode:\n%s', meta)

        return examples[RED], examples[BLUE], meta
