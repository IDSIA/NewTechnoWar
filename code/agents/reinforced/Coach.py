import logging
import os
import sys

import numpy as np
import ray

from collections import deque
from itertools import cycle
from datetime import datetime
from pickle import Pickler, Unpickler

import torch
from tqdm import tqdm

from core.const import RED, BLUE
from agents import Puppet, MatchManager
from agents.reinforced import MCTS
from agents.reinforced.nn import ModelWrapper
from core.game import GameBoard, GameState
from utils.copy import deepcopy

logger = logging.getLogger(__name__)


num_gpus = 1 if torch.cuda.is_available() else 0.0
logger.info('GPUs used by RAY: %s', num_gpus)


# note: wrapper functions are used to let the non-parallel option work without ray implementation


@ray.remote
def executeEpisodeWrapper(board, state, seed: int, args: tuple, temp_threshold):
    """This is a wrapper for the parallel execution."""
    return executeEpisode(board, state, seed, args, temp_threshold)


def executeEpisode(board, state, seed: int, args: tuple, temp_threshold):
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
    trainExamples_RED_Action = []
    trainExamples_RED_Response = []
    trainExamples_BLUE_Action = []
    trainExamples_BLUE_Response = []

    random = np.random.default_rng(seed)

    # puppets agents are used to train a MTCS both for RED and BLUE point of view
    puppet = {
        RED: Puppet(RED),
        BLUE: Puppet(BLUE),
    }
    mm = MatchManager('', puppet[RED], puppet[BLUE], board, deepcopy(state), seed, False)

    red_act, red_res, blue_act, blue_res, max_weapon_per_figure, max_figure_per_scenario, max_move_no_response_size, max_attack_size, num_MCTS_sims, cpuct = args

    mcts = MCTS(red_act, red_res, blue_act, blue_res, seed, max_weapon_per_figure, max_figure_per_scenario, max_move_no_response_size, max_attack_size, num_MCTS_sims, cpuct)

    episodeStep = 0
    cnt = 0
    start_time = datetime.now()

    try:
        while not mm.end:  # testing: cnt < 30:
            episodeStep += 1
            cnt += 1

            temp = int(episodeStep < temp_threshold)

            board = mm.board
            state = deepcopy(mm.state)
            action_type, team, _ = mm.nextPlayer()

            logger.info(f'Episode step: {episodeStep} action: {action_type}')

            if action_type in ('update', 'init', 'end'):
                mm.nextStep()
                continue

            action_type = 'Action' if action_type == 'round' else 'Response'

            logger.debug('Condition from coach BEFORE call getActionProb %s', state)

            _, valid_actions = mcts.actionIndexMapping(mm.gm, board, state, team, action_type)

            data_vector = mcts.generateFeatures(board, state)

            pi, _ = mcts.getActionProb(board, state, team, action_type, temp=temp)

            example = [data_vector, team, pi, None]

            if team == RED and action_type == "Action":
                trainExamples_RED_Action.append(example)
            if team == RED and action_type == "Response":
                trainExamples_RED_Response.append(example)
            if team == BLUE and action_type == "Action":
                trainExamples_BLUE_Action.append(example)
            if team == BLUE and action_type == "Response":
                trainExamples_BLUE_Response.append(example)

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

        # assign victory: 1 is winner, -1 is loser
        r, b = (1, -1) if mm.winner == RED else (-1, 1)

        end_time = datetime.now()

        logger.info('elapsed time: %s', (end_time - start_time))

        return (
            # board, team, pi, winner
            [(x[0], x[2], r) for x in trainExamples_RED_Action],
            [(x[0], x[2], r) for x in trainExamples_RED_Response],
            [(x[0], x[2], b) for x in trainExamples_BLUE_Action],
            [(x[0], x[2], b) for x in trainExamples_BLUE_Response]
        )
    except Exception as e:
        logger.error(f'Failed computation, reason {e}')
        logger.exception(e)
        return ([], [], [], [])


@ray.remote(num_gpus=num_gpus)
def trainModelWrapper(model: ModelWrapper, tr_examples_history: list, num_it_tr_examples_history: int, seed: int, folder_ceckpoint: str, i: int, team: str, action_type: str):
    trainModel(model, tr_examples_history, num_it_tr_examples_history, seed, folder_ceckpoint, i, team, action_type)


def trainModel(model: ModelWrapper, tr_examples_history: list, num_it_tr_examples_history: int, seed: int, folder_ceckpoint: str, i: int, team: str, action_type: str):

    if len(tr_examples_history) > num_it_tr_examples_history:
        logger.warning(f"Removing the oldest entry in trainExamples. len(tr_examples_history) = {len(tr_examples_history)}")
        tr_examples_history.pop(0)

    os.makedirs(folder_ceckpoint, exist_ok=True)

    r = np.random.default_rng(seed)

    # backup history to a file
    # NB! the examples were collected using the model from the previous iteration, so (i-1)
    iteration = i - 1

    # save previous model (current model before training)
    model.save_checkpoint(folder=folder_ceckpoint, filename=f'checkpoint_{iteration}_{team}_{action_type}.pth.tar')

    # save traing examples
    filename = os.path.join(folder_ceckpoint, f"checkpoint_{iteration}_{team}_{action_type}.examples")
    with open(filename, "wb+") as f:
        Pickler(f).dump(tr_examples_history)

    # shuffle examples before training
    train_examples = []
    for e in tr_examples_history:
        train_examples.extend(e)
    r.shuffle(train_examples)

    # training new network
    model.train(train_examples)

    # save new model
    model.save_checkpoint(folder=folder_ceckpoint, filename=f'new_{team}_{action_type}.pth.tar')

    logger.info('RED  Action   Losses Average %s', model.history[-1])

    # save losses history
    filename = os.path.join(folder_ceckpoint, f"checkpoint_{iteration}_{team}_{action_type}.losses.tsv")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\t'.join(['i', 'l_pi_avg', 'l_pi_count', 'l_pi_sum', 'l_pi_val', 'l_v_avg', 'l_v_count', 'l_v_sum', 'l_v_val']))
        f.write('\n')
        for x in range(len(model.history)):
            l_pi, l_v = model.history[x]
            f.write('\t'.join([str(a) for a in [x, l_pi.avg, l_pi.count, l_pi.sum, l_pi.val, l_v.avg, l_v.count, l_v.sum, l_v.val]]))
            f.write('\n')


class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined in Game and NeuralNet.
    """

    def __init__(self,
                 board: GameBoard,
                 state: GameState,
                 red_act: ModelWrapper,
                 red_res: ModelWrapper,
                 blue_act: ModelWrapper,
                 blue_res: ModelWrapper,
                 seed: int = 0,
                 num_iters: int = 1000,
                 num_eps: int = 100,
                 max_queue_len: int = 10,
                 max_weapon_per_figure: int = 8,
                 max_figure_per_scenario: int = 6,
                 max_move_no_response_size: int = 1351,
                 max_attack_size: int = 288,
                 num_MCTS_sims: int = 30,
                 cpuct: int = 1,
                 temp_threshold: int = 15,
                 parallel: bool = True,
                 num_it_tr_examples_history: int = 20,
                 folder_checkpoint: str = '.',
                 load_folder_file: str = './models'
                 ):
        self.board: GameBoard = board
        self.state: GameState = state

        self.seed: int = seed
        self.random = np.random.default_rng(self.seed)

        self.parallel: bool = parallel
        self.num_eps: int = num_eps
        self.num_iters: int = num_iters
        self.max_queue_len: int = max_queue_len
        self.num_it_tr_examples_history: int = num_it_tr_examples_history

        self.folder_ceckpoint = folder_checkpoint
        self.load_folder_file = load_folder_file

        self.max_weapon_per_figure = max_weapon_per_figure
        self.max_figure_per_scenario = max_figure_per_scenario
        self.max_move_no_response_size = max_move_no_response_size
        self.max_attack_size = max_attack_size
        self.num_MCTS_sims = num_MCTS_sims
        self.cpuct = cpuct
        self.temp_threshold = temp_threshold

        self.red_act: ModelWrapper = red_act
        self.red_res: ModelWrapper = red_res
        self.blue_act: ModelWrapper = blue_act
        self.blue_res: ModelWrapper = blue_res

        self.tr_examples_history_RED_Act = []
        self.tr_examples_history_RED_Res = []
        self.tr_examples_history_BLUE_Act = []
        self.tr_examples_history_BLUE_Res = []

        self.skip_first_self_play: bool = False  # can be overriden in loadTrainExamples()

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximum length of max_queue_len).
        """

        it_tr_examples_RED_Act = []
        it_tr_examples_RED_Res = []
        it_tr_examples_BLUE_Act = []
        it_tr_examples_BLUE_Res = []

        for i in range(1, self.num_iters + 1):
            # bookkeeping
            logger.info(f'Starting Iter #{i} ...')

            self.red_act.to('cpu')
            self.red_res.to('cpu')
            self.blue_act.to('cpu')
            self.blue_res.to('cpu')

            # examples of the iteration
            if not self.skip_first_self_play or i > 1:
                it_tr_examples = deque([], maxlen=self.max_queue_len)

                board = self.board
                state = self.state
                seed = self.seed
                tempThreshold = self.temp_threshold

                results = []

                logger.info('Sart Self Play #%s Iter #%s', len(self.tr_examples_history_RED_Act), i)

                mcts = (self.red_act, self.red_res, self.blue_act, self.blue_res, self.max_weapon_per_figure, self.max_figure_per_scenario, self.max_move_no_response_size,
                        self.max_attack_size, self. num_MCTS_sims, self.cpuct)

                if self.parallel:
                    # this uses ray's parallelism
                    tasks = []

                    for c in tqdm(range(self.num_eps), desc="Preparing"):
                        task = executeEpisodeWrapper.remote(board, state, seed + c, mcts, tempThreshold)
                        tasks.append(task)

                    for task in tqdm(tasks, desc="Self Play"):
                        results.append(ray.get(task))
                else:
                    # this uses single thread
                    for c in range(self.num_eps):
                        ite_R_A, ite_R_R, ite_B_A, ite_B_R = executeEpisode(board, state, seed + c, mcts, tempThreshold)
                        results.append((ite_R_A, ite_R_R, ite_B_A, ite_B_R))

                for ite_R_A, ite_R_R, ite_B_A, ite_B_R in results:
                    it_tr_examples_RED_Act += ite_R_A
                    it_tr_examples_RED_Res += ite_R_R
                    it_tr_examples_BLUE_Act += ite_B_A
                    it_tr_examples_BLUE_Res += ite_B_R

                # save the iteration examples to the history
                self.tr_examples_history_RED_Act.append(it_tr_examples_RED_Act)
                self.tr_examples_history_RED_Res.append(it_tr_examples_RED_Res)
                self.tr_examples_history_BLUE_Act.append(it_tr_examples_BLUE_Act)
                self.tr_examples_history_BLUE_Res.append(it_tr_examples_BLUE_Res)

                logger.info('End Self Play #%s Iter #%s', len(self.tr_examples_history_RED_Act), i)

            logger.info('Start training Iter #%s ...', i)

            if torch.cuda.is_available():
                logger.info('Using cuda as devices for training')
                devices = cycle(f'cuda:{n}' for n in range(torch.cuda.device_count()))

                self.red_act.to(next(devices))
                self.red_res.to(next(devices))
                self.blue_act.to(next(devices))
                self.blue_res.to(next(devices))
            else:
                logger.info('Using CPU as devices for training')

                self.red_act.to('cpu')
                self.red_res.to('cpu')
                self.blue_act.to('cpu')
                self.blue_res.to('cpu')

            if self.parallel:
                tasks = [
                    trainModelWrapper.remote(self.red_act, self.tr_examples_history_RED_Act, self.num_it_tr_examples_history, self.seed, self.folder_ceckpoint, i, RED, 'Act'),
                    trainModelWrapper.remote(self.red_res, self.tr_examples_history_RED_Res, self.num_it_tr_examples_history, self.seed, self.folder_ceckpoint, i, RED, 'Res'),
                    trainModelWrapper.remote(self.blue_act, self.tr_examples_history_BLUE_Act, self.num_it_tr_examples_history, self.seed, self.folder_ceckpoint, i, BLUE, 'Act'),
                    trainModelWrapper.remote(self.blue_res, self.tr_examples_history_BLUE_Res, self.num_it_tr_examples_history, self.seed, self.folder_ceckpoint, i, BLUE, 'Res')
                ]
                for task in tqdm(tasks, desc="Training"):
                    ray.get(task)
            else:
                trainModel(self.red_act, self.tr_examples_history_RED_Act, self.num_it_tr_examples_history, self.seed, self.folder_ceckpoint, i, RED, 'Act'),
                trainModel(self.red_res, self.tr_examples_history_RED_Res, self.num_it_tr_examples_history, self.seed, self.folder_ceckpoint, i, RED, 'Res'),
                trainModel(self.blue_act, self.tr_examples_history_BLUE_Act, self.num_it_tr_examples_history, self.seed, self.folder_ceckpoint, i, BLUE, 'Act'),
                trainModel(self.blue_res, self.tr_examples_history_BLUE_Res, self.num_it_tr_examples_history, self.seed, self.folder_ceckpoint, i, BLUE, 'Res')

    def loadTrainExamples(self):
        modelFile = os.path.join(self.load_folder_file)
        examplesFile = modelFile + ".examples"
        if not os.path.isfile(examplesFile):
            logger.warning(f'File "{examplesFile}" with trainExamples not found!')
            r = input("Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            logger.info("File with trainExamples found. Loading it...")
            with open(examplesFile, "rb") as f:
                self.tr_examples_history_RED_Act = Unpickler(f).load()
            logger.info('Loading done!')
            with open(examplesFile, "rb") as f:
                self.tr_examples_history_RED_Res = Unpickler(f).load()
            logger.info('Loading done!')
            with open(examplesFile, "rb") as f:
                self.tr_examples_history_BLUE_Act = Unpickler(f).load()
            logger.info('Loading done!')
            with open(examplesFile, "rb") as f:
                self.tr_examples_history_BLUE_Res = Unpickler(f).load()
            logger.info('Loading done!')

            # examples based on the model were already collected (loaded)
            self.skip_first_self_play = True
