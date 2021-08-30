# Coach
import logging
import os
import sys

import numpy as np
import ray

from collections import deque
from datetime import datetime
from pickle import Pickler, Unpickler
from tqdm import tqdm

from core.const import RED, BLUE
from agents.adversarial.puppets import Puppet
from agents.matchmanager import MatchManager
from agents.reinforced.MCTS import MCTS
from utils.copy import deepcopy

logger = logging.getLogger(__name__)


@ray.remote
def executeEpisodeWrapper(board, state, seed: int, mcts: MCTS, tempThreshold):
    """This is a wrapper for the parallel execution."""
    return executeEpisode(board, state, seed, mcts, tempThreshold)


def executeEpisode(board, state, seed: int, mcts: MCTS, tempThreshold):
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

        temp = int(episodeStep < tempThreshold)

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
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """

    def __init__(self, board, state, nnet_RED_Act, nnet_RED_Res, nnet_BLUE_Act, nnet_BLUE_Res, args):
        self.board = board
        self.state = state

        self.seed = args.seed
        self.random = np.random.default_rng(self.seed)

        self.nnet_RED_Act = nnet_RED_Act
        self.nnet_RED_Res = nnet_RED_Res
        self.nnet_BLUE_Act = nnet_BLUE_Act
        self.nnet_BLUE_Res = nnet_BLUE_Res

        self.args = args

        self.trainExamplesHistory_RED_Act = []
        self.trainExamplesHistory_RED_Res = []
        self.trainExamplesHistory_BLUE_Act = []
        self.trainExamplesHistory_BLUE_Res = []

        self.skipFirstSelfPlay = False  # can be overriden in loadTrainExamples()

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximum length of maxlenofQueue).
        """

        iterationTrainExamples_RED_Act = []
        iterationTrainExamples_RED_Res = []
        iterationTrainExamples_BLUE_Act = []
        iterationTrainExamples_BLUE_Res = []

        for i in range(1, self.args.numIters + 1):
            # bookkeeping
            logger.info(f'Starting Iter #{i} ...')
            # examples of the iteration
            if not self.skipFirstSelfPlay or i > 1:
                iterationTrainExamples = deque([], maxlen=self.args.maxlenOfQueue)

                mcts = MCTS(self.nnet_RED_Act, self.nnet_RED_Res, self.nnet_BLUE_Act, self.nnet_BLUE_Res, self.args)

                board = self.board
                state = self.state
                seed = self.seed
                tempThreshold = self.args.tempThreshold

                results = []

                if self.args.parallel:
                    # this uses ray's parallelism
                    tasks = []

                    for c in range(self.args.numEps):
                        task = executeEpisodeWrapper.remote(board, state, seed + c, mcts, tempThreshold)
                        tasks.append(task)

                    for task in tqdm(tasks, desc="Self Play"):
                        results.append(ray.get(task))
                else:
                    # this uses single thread
                    for c in range(self.args.numEps):
                        ite_R_A, ite_R_R, ite_B_A, ite_B_R = executeEpisode(board, state, seed + c, mcts, tempThreshold)

                for ite_R_A, ite_R_R, ite_B_A, ite_B_R in results:
                    iterationTrainExamples_RED_Act += ite_R_A
                    iterationTrainExamples_RED_Res += ite_R_R
                    iterationTrainExamples_BLUE_Act += ite_B_A
                    iterationTrainExamples_BLUE_Res += ite_B_R

                # save the iteration examples to the history
                self.trainExamplesHistory_RED_Act.append(iterationTrainExamples_RED_Act)
                self.trainExamplesHistory_RED_Res.append(iterationTrainExamples_RED_Res)
                self.trainExamplesHistory_BLUE_Act.append(iterationTrainExamples_BLUE_Act)
                self.trainExamplesHistory_BLUE_Res.append(iterationTrainExamples_BLUE_Res)

                logger.info('END Self Play %s', len(self.trainExamplesHistory_RED_Act))

            if len(self.trainExamplesHistory_RED_Act) > self.args.numItersForTrainExamplesHistory:
                logger.warning(
                    f"Removing the oldest entry in trainExamples. len(trainExamplesHistory) = {len(self.trainExamplesHistory_RED_Act)}")
                self.trainExamplesHistory_RED_Act.pop(0)
            if len(self.trainExamplesHistory_RED_Res) > self.args.numItersForTrainExamplesHistory:
                logger.warning(
                    f"Removing the oldest entry in trainExamples. len(trainExamplesHistory) = {len(self.trainExamplesHistory_RED_Res)}")
                self.trainExamplesHistory_RED_Res.pop(0)
            if len(self.trainExamplesHistory_BLUE_Act) > self.args.numItersForTrainExamplesHistory:
                logger.warning(
                    f"Removing the oldest entry in trainExamples. len(trainExamplesHistory) = {len(self.trainExamplesHistory_BLUE_Act)}")
                self.trainExamplesHistory_BLUE_Act.pop(0)
            if len(self.trainExamplesHistory_BLUE_Res) > self.args.numItersForTrainExamplesHistory:
                logger.warning(
                    f"Removing the oldest entry in trainExamples. len(trainExamplesHistory) = {len(self.trainExamplesHistory_BLUE_Res)}")
                self.trainExamplesHistory_BLUE_Res.pop(0)
            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)
            self.saveTrainExamples(i - 1)

            # shuffle RED Action examples before training
            trainExamples_RED_Act = []
            for e in self.trainExamplesHistory_RED_Act:
                trainExamples_RED_Act.extend(e)
            self.random.shuffle(trainExamples_RED_Act)

            # shuffle RED Response examples before training
            trainExamples_RED_Res = []
            for e in self.trainExamplesHistory_RED_Res:
                trainExamples_RED_Res.extend(e)
            self.random.shuffle(trainExamples_RED_Res)

            # shuffle BLUE Action examples before training
            trainExamples_BLUE_Act = []
            for e in self.trainExamplesHistory_BLUE_Act:
                trainExamples_BLUE_Act.extend(e)
            self.random.shuffle(trainExamples_BLUE_Act)

            # shuffle BLUE Action examples before training
            trainExamples_BLUE_Res = []
            for e in self.trainExamplesHistory_BLUE_Res:
                trainExamples_BLUE_Res.extend(e)
            self.random.shuffle(trainExamples_BLUE_Res)

            # training new networks

            self.nnet_RED_Act.train(trainExamples_RED_Act)
            self.nnet_RED_Act.save_checkpoint(folder=self.args.checkpoint, filename='new_RED_Act.pth.tar')
            logger.info('RED  Action   Losses Average %s', self.nnet_RED_Act.history[-1])

            self.nnet_RED_Res.train(trainExamples_RED_Res)
            self.nnet_RED_Res.save_checkpoint(folder=self.args.checkpoint, filename='new_RED_Res.pth.tar')
            logger.info('RED  Response Losses Average %s', self.nnet_RED_Res.history[-1])

            self.nnet_BLUE_Act.train(trainExamples_BLUE_Act)
            self.nnet_BLUE_Act.save_checkpoint(folder=self.args.checkpoint, filename='new_BLUE_Act.pth.tar')
            logger.info('BLUE Action   Losses Average %s', self.nnet_BLUE_Act.history[-1])

            self.nnet_BLUE_Res.train(trainExamples_BLUE_Res)
            self.nnet_BLUE_Res.save_checkpoint(folder=self.args.checkpoint, filename='new_BLUE_Res.pth.tar')
            logger.info('BLUE Response Losses Average %s', self.nnet_BLUE_Res.history[-1])

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def saveTrainExamples(self, iteration):
        folder = self.args.checkpoint
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + "_RED_Act.examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory_RED_Act)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + "_RED_Res.examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory_RED_Res)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + "_BLUE_Act.examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory_BLUE_Act)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + "_BLUE_Res.examples")
        with open(filename, "wb+") as f:
            Pickler(f).dump(self.trainExamplesHistory_BLUE_Res)
        f.closed

    def loadTrainExamples(self):
        modelFile = os.path.join(self.args.load_folder_file)
        examplesFile = modelFile + ".examples"
        if not os.path.isfile(examplesFile):
            logger.warning(f'File "{examplesFile}" with trainExamples not found!')
            r = input("Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            logger.info("File with trainExamples found. Loading it...")
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory_RED_Act = Unpickler(f).load()
            logger.info('Loading done!')
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory_RED_Res = Unpickler(f).load()
            logger.info('Loading done!')
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory_BLUE_Act = Unpickler(f).load()
            logger.info('Loading done!')
            with open(examplesFile, "rb") as f:
                self.trainExamplesHistory_BLUE_Res = Unpickler(f).load()
            logger.info('Loading done!')

            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True
