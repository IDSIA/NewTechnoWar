# Coach

import logging
import os
import sys
from collections import deque
from pickle import Pickler, Unpickler
from random import shuffle

import numpy as np
from tqdm import tqdm

import core
from core.game import GameManager, goalAchieved
from core.const import RED, BLUE
from core.actions import Attack, Move, Action, Response, NoResponse, PassTeam, AttackResponse, NoResponse, PassFigure

from agents.reinforced.MCTS import MCTS
from agents.reinforced.utils import calculateValidMoves, WEAPONS_INDICES


logger = logging.getLogger(__name__)


class Coach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """

    def __init__(self, board, state, team, moveType, nnet_RED_Act, nnet_RED_Res, nnet_BLUE_Act, nnet_BLUE_Res, args):
        self.board = board
        self.state = state
        self.team = team
        self.moveType = moveType

        self.gm = GameManager()

        self.nnet_RED_Act = nnet_RED_Act
        self.nnet_RED_Res = nnet_RED_Res
        self.nnet_BLUE_Act = nnet_BLUE_Act
        self.nnet_BLUE_Res = nnet_BLUE_Res
        self.args = args
        self.mcts = MCTS(board, state, team, moveType, nnet_RED_Act, nnet_RED_Res, nnet_BLUE_Act, nnet_BLUE_Res, args)

        self.trainExamplesHistory_RED_Act = []
        self.trainExamplesHistory_RED_Res = []
        self.trainExamplesHistory_BLUE_Act = []
        self.trainExamplesHistory_BLUE_Res = []

        self.skipFirstSelfPlay = False  # can be overriden in loadTrainExamples()

        self.maxWeaponPerFigure = args.maxWeaponPerFigure
        self.maxFigurePerScenario = args.maxFigurePerScenario
        self.maxMoveNoResponseSize = args.maxMoveNoResponseSize
        self.maxActionSize = args.maxMoveNoResponseSize + args.maxAttackSize

    def actionIndexMappingCoach(self, allValidActions):  # TODO: consider Wait actions if needed

        validActionIndicesWrtAllActions = [0] * self.maxActionSize  # [0]*5851 #self.numMaxActions(board, state)
        validActionWrtAllActions = [None] * self.maxActionSize  # [None]*5851 #self.numMaxActions(board, state)

        if allValidActions != []:

            for a in allValidActions:
                idx = -1

                if type(a) == AttackResponse:

                    figure_ind = a.figure_id
                    target_ind = a.target_id

                    weapon_ind = WEAPONS_INDICES[a.weapon_id]

                    idx = (
                        self.maxMoveNoResponseSize +
                        weapon_ind +
                        target_ind * self.maxWeaponPerFigure +
                        figure_ind * self.maxWeaponPerFigure * self.maxFigurePerScenario
                    )

                elif type(a) == NoResponse:

                    idx = self.maxMoveNoResponseSize - 1

                    # validActionIndicesWrtAllActions[5850] = 1
                    # validActionWrtAllActions[5850] = a

                else:

                    if type(a) == PassFigure:
                        x = 0
                        y = 0

                    # elif type(a) == core.actions.attacks.Attack: # TODO: add weapons

                    #     start_pos = a.position.tuple()
                    #     end_pos = a.destination.tuple()

                    #     x = end_pos[0] - start_pos[0]
                    #     y = end_pos[1] - start_pos[1]

                    # elif type(a) == core.actions.movements.AttackGround: # TODO: add weapons

                    #     start_pos = a.position.tuple()
                    #     end_pos = a.destination.tuple()

                    #     x = end_pos[0] - start_pos[0]
                    #     y = end_pos[1] - start_pos[1]

                    elif type(a) == core.actions.movements.Move:

                        start_pos = a.position.tuple()
                        end_pos = a.destination.tuple()

                        x = end_pos[0] - start_pos[0]
                        y = end_pos[1] - start_pos[1]

                    elif type(a) == core.actions.movements.MoveLoadInto:

                        start_pos = a.position.tuple()
                        end_pos = a.destination.tuple()

                        x = end_pos[0] - start_pos[0]
                        y = end_pos[1] - start_pos[1]

                    figure_index = a.figure_id

                    if x + y <= 0:
                        index_shift = ((x + y + 14) * (x + y + 15)) // 2 + y + 7
                    else:
                        index_shift = 224 - (((x + y - 14) * (x + y - 15)) // 2 - y - 7)

                    idx = figure_index * 225 + index_shift

                validActionIndicesWrtAllActions[idx] = 1
                validActionWrtAllActions[idx] = a

        return validActionIndicesWrtAllActions, validActionWrtAllActions

    def executeEpisode(self):
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
        self.team = RED
        self.moveType = "Action"
        episodeStep = 0

        cnt = 0

        while True:  # testing: cnt < 30:
            episodeStep += 1
            cnt += 1

            temp = int(episodeStep < self.args.tempThreshold)

            print('condition from coach BEFORE call getActionProb', self.state)

            allValidActions = calculateValidMoves(self.board, self.state, self.team, self.moveType)

            pi, s_ret = self.mcts.getActionProb(self.board, self.state, self.team, self.moveType, temp=temp)

            example = [self.board, self.team, pi, None]

            if self.team == RED and self.moveType == "Action":
                trainExamples_RED_Action.append(example)
            if self.team == RED and self.moveType == "Response":
                trainExamples_RED_Response.append(example)
            if self.team == BLUE and self.moveType == "Action":
                trainExamples_BLUE_Action.append(example)
            if self.team == BLUE and self.moveType == "Response":
                trainExamples_BLUE_Response.append(example)

            if max(pi) == 1:
                action_index = np.argmax(pi)
                logger.warn(f'Unexpected single choice! Index: {action_index}')
            else:
                action_index = np.random.choice(len(pi), p=pi)

            print(pi)
            print(action_index)

            allValidActions = calculateValidMoves(self.board, self.state, self.team, self.moveType)

            _, validActions = self.actionIndexMappingCoach(allValidActions)

            if allValidActions == [] and action_index == self.maxMoveNoResponseSize:
                validActions[self.maxMoveNoResponseSize] = PassTeam(self.team)

            # TODO: what follows there is what the MatchManager already does. How to use it in this context?

            if self.team == RED and self.moveType == "Action" and action_index != self.maxMoveNoResponseSize:
                self.team = BLUE
                self.moveType = "Response"
            elif self.team == RED and self.moveType == "Action" and action_index == self.maxMoveNoResponseSize:
                self.team = BLUE
                self.moveType = "Action"
            elif self.team == RED and self.moveType == "Response":
                # if validActions == []:
                #     # if we are at the end of a turn, need to update and then go to next ....
                #     self.gm.update(state)
                #     allValidActions = calculateValidMoves(self.board, self.state, self.team, self.moveType)
                #     valids, validActions = self.actionIndexMapping(allValidActions)

                self.team = RED
                self.moveType = "Action"

            elif self.team == BLUE and self.moveType == "Action" and action_index != self.maxMoveNoResponseSize:
                self.team = RED
                self.moveType = "Response"
            elif self.team == BLUE and self.moveType == "Action" and action_index == self.maxMoveNoResponseSize:
                self.team = RED
                self.moveType = "Action"
            elif self.team == BLUE and self.moveType == "Response":
                self.team = BLUE
                self.moveType = "Action"

            if allValidActions == [] and action_index != self.maxMoveNoResponseSize:
                self.gm.update(self.state)
                self.team = RED
                self.moveType = "Action"
            else:
                action = validActions[action_index]
                next_s, _ = self.gm.activate(self.board, self.state, action)
                self.state = next_s

            isEnd, winner = goalAchieved(self.board, self.state)

            if not isEnd:
                r = 0
            elif winner == self.team:
                r = 1
            else:
                r = -1

            if r != 0:
                return [(x[0], x[2], r * ((-1) ** (x[1] != self.team))) for x in trainExamples_RED_Action], [(x[0], x[2], r * ((-1) ** (x[1] != self.team))) for x in trainExamples_RED_Response], [(x[0], x[2], r * ((-1) ** (x[1] != self.team))) for x in trainExamples_BLUE_Action], [(x[0], x[2], r * ((-1) ** (x[1] != self.team))) for x in trainExamples_BLUE_Response]

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

                cntC = 0
                for _ in tqdm(range(self.args.numEps), desc="Self Play"):
                    self.mcts = MCTS(self.board, self.state, self.team, self.moveType, self.nnet_RED_Act, self.nnet_RED_Res, self.nnet_BLUE_Act, self.nnet_BLUE_Res, self.args)
                    print('END MCTS', cntC)
                    (ite_R_A, ite_R_R, ite_B_A, ite_B_R) = self.executeEpisode()
                    print('END executeEpisode', cntC)
                    cntC += 1
                    iterationTrainExamples_RED_Act += ite_R_A
                    iterationTrainExamples_RED_Res += ite_R_R
                    iterationTrainExamples_BLUE_Act += ite_B_A
                    iterationTrainExamples_BLUE_Res += ite_B_R

                # save the iteration examples to the history
                self.trainExamplesHistory_RED_Act.append(iterationTrainExamples_RED_Act)
                self.trainExamplesHistory_RED_Res.append(iterationTrainExamples_RED_Res)
                self.trainExamplesHistory_BLUE_Act.append(iterationTrainExamples_BLUE_Act)
                self.trainExamplesHistory_BLUE_Res.append(iterationTrainExamples_BLUE_Res)

                print('END Self Play', len(self.trainExamplesHistory_RED_Act))

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
            shuffle(trainExamples_RED_Act)

            # shuffle RED Response examples before training
            trainExamples_RED_Res = []
            for e in self.trainExamplesHistory_RED_Res:
                trainExamples_RED_Res.extend(e)
            shuffle(trainExamples_RED_Res)

            # shuffle BLUE Action examples before training
            trainExamples_BLUE_Act = []
            for e in self.trainExamplesHistory_BLUE_Act:
                trainExamples_BLUE_Act.extend(e)
            shuffle(trainExamples_BLUE_Act)

            # shuffle BLUE Action examples before training
            trainExamples_BLUE_Res = []
            for e in self.trainExamplesHistory_BLUE_Res:
                trainExamples_BLUE_Res.extend(e)
            shuffle(trainExamples_BLUE_Res)

            # training new networks

            self.nnet_RED_Act.train(trainExamples_RED_Act)
            self.nnet_RED_Act.save_checkpoint(folder=self.args.checkpoint, filename='new_RED_Act.pth.tar')

            self.nnet_RED_Res.train(trainExamples_RED_Res)
            self.nnet_RED_Res.save_checkpoint(folder=self.args.checkpoint, filename='new_RED_Res.pth.tar')

            self.nnet_BLUE_Act.train(trainExamples_BLUE_Act)
            self.nnet_BLUE_Act.save_checkpoint(folder=self.args.checkpoint, filename='new_BLUE_Act.pth.tar')

            self.nnet_BLUE_Res.train(trainExamples_BLUE_Res)
            self.nnet_BLUE_Res.save_checkpoint(folder=self.args.checkpoint, filename='new_BLUE_Res.pth.tar')

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
