import logging
import os
import sys

import numpy as np
import ray

from collections import deque
from datetime import datetime
from pickle import Pickler, Unpickler
from tqdm import tqdm

from agents.reinforced.nn.NNet import NNetWrapper
from agents.reinforced.consts import FRAC_GPUS

from core.const import RED, BLUE
from agents.adversarial.puppets import Puppet
from agents.matchmanager import MatchManager
from agents.reinforced.MCTS import MCTS
from core.game.board import GameBoard
from core.game.state import GameState
from utils.copy import deepcopy

logger = logging.getLogger(__name__)


@ray.remote(num_gpus=FRAC_GPUS)
def executeEpisodeWrapper(board, state, seed: int, mcts: MCTS, temp_threshold):
    """This is a wrapper for the parallel execution."""
    return executeEpisode(board, state, seed, mcts, temp_threshold)


def executeEpisode(board, state, seed: int, mcts: MCTS, temp_threshold):
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

    episodeStep = 0
    cnt = 0
    start_time = datetime.now()

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

        data_vector = mcts.generateBoard(board, state)

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


class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined in Game and NeuralNet.
    """

    def __init__(self,
                 board: GameBoard,
                 state: GameState,
                 red_act: NNetWrapper,
                 red_res: NNetWrapper,
                 blue_act: NNetWrapper,
                 blue_res: NNetWrapper,
                 seed: int = 0,
                 epochs: int = 2,
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

        self.red_act: NNetWrapper = red_act
        self.red_res: NNetWrapper = red_res
        self.blue_act: NNetWrapper = blue_act
        self.blue_res: NNetWrapper = blue_res

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
            # examples of the iteration
            if not self.skip_first_self_play or i > 1:
                it_tr_examples = deque([], maxlen=self.max_queue_len)

                mcts = MCTS(
                    self.red_act, self.red_res, self.blue_act, self.blue_res,
                    self.seed, self.max_weapon_per_figure, self.max_figure_per_scenario, self.max_move_no_response_size,
                    self.max_attack_size, self. num_MCTS_sims, self.cpuct
                )

                board = self.board
                state = self.state
                seed = self.seed
                tempThreshold = self.temp_threshold

                results = []

                if self.parallel:
                    # this uses ray's parallelism
                    tasks = []

                    for c in range(self.num_eps):
                        task = executeEpisodeWrapper.remote(board, state, seed + c, mcts, tempThreshold)
                        tasks.append(task)

                    for task in tqdm(tasks, desc="Self Play"):
                        results.append(ray.get(task))
                else:
                    # this uses single thread
                    for c in range(self.num_eps):
                        ite_R_A, ite_R_R, ite_B_A, ite_B_R = executeEpisode(board, state, seed + c, mcts, tempThreshold)

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

                logger.info('END Self Play %s', len(self.tr_examples_history_RED_Act))

            if len(self.tr_examples_history_RED_Act) > self.num_it_tr_examples_history:
                logger.warning(f"Removing the oldest entry in trainExamples. len(tr_examples_history) = {len(self.tr_examples_history_RED_Act)}")
                self.tr_examples_history_RED_Act.pop(0)
            if len(self.tr_examples_history_RED_Res) > self.num_it_tr_examples_history:
                logger.warning(f"Removing the oldest entry in trainExamples. len(tr_examples_history) = {len(self.tr_examples_history_RED_Res)}")
                self.tr_examples_history_RED_Res.pop(0)
            if len(self.tr_examples_history_BLUE_Act) > self.num_it_tr_examples_history:
                logger.warning(f"Removing the oldest entry in trainExamples. len(tr_examples_history) = {len(self.tr_examples_history_BLUE_Act)}")
                self.tr_examples_history_BLUE_Act.pop(0)
            if len(self.tr_examples_history_BLUE_Res) > self.num_it_tr_examples_history:
                logger.warning(f"Removing the oldest entry in trainExamples. len(tr_examples_history) = {len(self.tr_examples_history_BLUE_Res)}")
                self.tr_examples_history_BLUE_Res.pop(0)

            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)
            self.saveTrainExamples(i - 1)

            # shuffle RED Action examples before training
            trainExamples_RED_Act = []
            for e in self.tr_examples_history_RED_Act:
                trainExamples_RED_Act.extend(e)
            self.random.shuffle(trainExamples_RED_Act)

            # shuffle RED Response examples before training
            trainExamples_RED_Res = []
            for e in self.tr_examples_history_RED_Res:
                trainExamples_RED_Res.extend(e)
            self.random.shuffle(trainExamples_RED_Res)

            # shuffle BLUE Action examples before training
            trainExamples_BLUE_Act = []
            for e in self.tr_examples_history_BLUE_Act:
                trainExamples_BLUE_Act.extend(e)
            self.random.shuffle(trainExamples_BLUE_Act)

            # shuffle BLUE Action examples before training
            trainExamples_BLUE_Res = []
            for e in self.tr_examples_history_BLUE_Res:
                trainExamples_BLUE_Res.extend(e)
            self.random.shuffle(trainExamples_BLUE_Res)

            # training new networks

            self.red_act.train(trainExamples_RED_Act)
            self.red_act.save_checkpoint(folder=self.folder_ceckpoint, filename='new_RED_Act.pth.tar')
            logger.info('RED  Action   Losses Average %s', self.red_act.history[-1])

            self.red_res.train(trainExamples_RED_Res)
            self.red_res.save_checkpoint(folder=self.folder_ceckpoint, filename='new_RED_Res.pth.tar')
            logger.info('RED  Response Losses Average %s', self.red_res.history[-1])

            self.blue_act.train(trainExamples_BLUE_Act)
            self.blue_act.save_checkpoint(folder=self.folder_ceckpoint, filename='new_BLUE_Act.pth.tar')
            logger.info('BLUE Action   Losses Average %s', self.blue_act.history[-1])

            self.blue_res.train(trainExamples_BLUE_Res)
            self.blue_res.save_checkpoint(folder=self.folder_ceckpoint, filename='new_BLUE_Res.pth.tar')
            logger.info('BLUE Response Losses Average %s', self.blue_res.history[-1])

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.folder_ceckpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + "_RED_Act.examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.tr_examples_history_RED_Act)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + "_RED_Res.examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.tr_examples_history_RED_Res)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + "_BLUE_Act.examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.tr_examples_history_BLUE_Act)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + "_BLUE_Res.examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.tr_examples_history_BLUE_Res)
        f.closed

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
