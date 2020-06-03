import random
import time
import math

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

from core import ACTION_MOVE
from core.state import StateOfTheBoard
from learningParameters import DEVICE


class Parameters:

    def __init__(self, team: str, params: dict):
        self.team = team
        self.params = params
        # here well probably put a neural net or similar.


class RandomAgent:

    def __init__(self, roundOfPlay: int, parameters: Parameters):
        self.roundOfPlay = roundOfPlay
        self.parameters = parameters
        self.team = parameters.team

    # must implement an update method.

    # select eps greedy action with eps decay
    # def select_action(self, self.state, self.steps_done):
    #    sample = random.random()
    #   eps_threshold = EPS_END + (EPS_START - EPS_END) * \
    #   math.exp(-1. * steps_done / EPS_DECAY)
    #   steps_done += 1
    # if sample > eps_threshold:
    #     with torch.no_grad():
    #         return pNN(state).max(1)[1].view(1, 1), steps_done
    # else:
    #     return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long), steps_done

    # select random action
    def selectAction(self, stateOfTheBoard, steps_done):#steps_done is NOT a member for performance
        #structure of action choice should be probably as follows:
        #1) choose a figure.
        #2) choose if to attack or move
        #2a) if attack: choose whom to attack, according to game rules like line of sight and similar
        #2b) if move: choose where to move, according to game rulse like roads and board boundaries

        #at the moment all this is implemented in terms of fully random actions, in a dummy code
        #in the real setup this is going to be too inefficient probably. will have to think of different representation
        lenFigures = len(stateOfTheBoard.figures[self.team])
        lenMoves = len(stateOfTheBoard.actionMoves)
        lenAttacks = len(stateOfTheBoard.actionAttacks[self.team])

        chosenFigure = torch.tensor([[random.randrange(lenFigures)]], device=DEVICE, dtype=torch.long)
        chosenAttackOrMove = torch.tensor([[random.randrange(2)]], device=DEVICE, dtype=torch.long)
        if ACTION_MOVE == ACTION_MOVE:
            chosenAction = torch.tensor([[random.randrange(lenMoves)]], device=DEVICE, dtype=torch.long)
        else:
            chosenAction = torch.tensor([[random.randrange(lenAttacks)]], device=DEVICE, dtype=torch.long)

        steps_done += 1
        #
        return chosenFigure, chosenAttackOrMove, chosenAction, steps_done





class MinMaxAgent:

    def __init__(self, roundOfPlay: int, parameters: Parameters):

        self.roundOfPlay = roundOfPlay
        self.team = parameters.team
        self.winValue =1
        self.lossValue = -1
        self.cache = {}
    
    def _flipTeam(self, team):
        if(team=='red'):
            return 'blue'
        elif(team=='blue'):
            return 'red'
        else:
            raise ValueError("Team must be: 'blue' or 'red'")

    def _max(self, stateOfTheBoard: StateOfTheBoard):
        """
        Evaluate the position `stateOfTheBoard` from the Maximizing player's point of view.

        :param board: The board position to evaluate
        :return: Tuple of (Best Result, Best Move in this situation). Returns -1 for best move if the game has already
        finished
        """

        board_hash = stateOfTheBoard.hashValue()
        if board_hash in self.cache:
            return self.cache[board_hash]

        
        max_value = self.lossValue
        action = (-1,-1)

        # If the game has already finished we return. Otherwise we compute
        winner = stateOfTheBoard.whoWon()
        if winner == self.team:
            print(str(self.team) + '_____won')
            max_value = self.winValue
            action = (-1,-1)
        elif winner == self._flipTeam(self.team):
            max_value = self.lossValue
            action = (-1,-1)
        else:
            for chosenFigure in range(0,len(stateOfTheBoard.figures[self.team])):
                for chosenMove in range(0,len(stateOfTheBoard.actionMoves)):
                    b = StateOfTheBoard(shape = stateOfTheBoard.shape, turn = stateOfTheBoard.turn, board = stateOfTheBoard.board, figures = stateOfTheBoard.figures)
                    legal = b.step(self.team, chosenFigure, ACTION_MOVE, chosenMove)
                    if legal[0]:#checks if the b.step was actually a legal action/move
                        b.update()
                        print('depth')
                        print(b.turn)
                        res, _ = self._min(b)
                        if res > max_value or action == (-1,-1):
                            max_value = res
                            action = (chosenFigure, chosenMove)

                        # Shortcut: Can't get better than that, so abort here and return this move
                        if max_value == self.winValue:
                            self.cache[board_hash] = (max_value, action)
                            return max_value, action

                        self.cache[board_hash] = (max_value, action)
        return max_value, action


    def _min(self, stateOfTheBoard: StateOfTheBoard):
        """
        Evaluate the board position `stateOfTheBoard` from the Minimizing player's point of view.

        :param board: The board position to evaluate
        :return: Tuple of (Best Result, Best Move in this situation). Returns -1 for best move if the game has already
        finished
        """

        board_hash = stateOfTheBoard.hashValue()
        if board_hash in self.cache:
            return self.cache[board_hash]

        min_value = self.winValue
        action = (-1,-1)

        # If the game has already finished we return. Otherwise we compute
        winner = stateOfTheBoard.whoWon()
        
        if winner == self.team:
            print('winner____________-' + str(winner))
            min_value = self.winValue
            action = (-1,-1)
        elif winner == self._flipTeam(self.team):
            print('winner____________-' + str(winner))
            min_value = self.lossValue
            action = (-1,-1)
        else:
            for chosenFigure in range(0,len(stateOfTheBoard.figures[self._flipTeam(self.team)])):
                for chosenMove in range(0,len(stateOfTheBoard.actionMoves)):
                    b = StateOfTheBoard(stateOfTheBoard.shape, stateOfTheBoard.turn, stateOfTheBoard.board, stateOfTheBoard.figures)
                    legal = b.step(self._flipTeam(self.team), chosenFigure, ACTION_MOVE, chosenMove)
                    if legal[0]:
                        res, _ = self._max(b)
                        if res < min_value or action == (-1,-1):
                            min_value = res
                            action = (chosenFigure,chosenMove)

                            # Shortcut: Can't get better than that, so abort here and return this move
                        if min_value == self.lossValue:
                            self.cache[board_hash] = (min_value, action)
                            return min_value, action

                        self.cache[board_hash] = (min_value, action)
        return min_value, action

    def selectAction(self, stateOfTheBoard, steps_done):#steps_done is NOT a member for performance
        
        score, action = self._max(stateOfTheBoard)
        print('Score__' + str(score))
        steps_done += 1
        
        chosenFigure = action[0]
        chosenAction = action[1]
        return chosenFigure, ACTION_MOVE, chosenAction, steps_done



class AlphaBetaAgent:

    def __init__(self, roundOfPlay: int, parameters: Parameters, maxSearchTime: int = 60, maxDepth: int = 15):

        self.roundOfPlay = roundOfPlay
        self.team = parameters.team
        self.winValue =1
        self.lossValue = -1
        self.maxDepth =  maxDepth
        self.maxSearchtime = maxSearchTime
        self.cache = {}
    
    def _flipTeam(self, team):
        if(team=='red'):
            return 'blue'
        elif(team=='blue'):
            return 'red'
        else:
            raise ValueError("Team must be: 'blue' or 'red'")
            


    def _max(self, stateOfTheBoard: StateOfTheBoard, alpha, beta, depth, maxRoundDepth):

        #check if hashed
        board_hash = stateOfTheBoard.hashValue()
        if board_hash in self.cache:
            return self.cache[board_hash]
        
        max_value = -math.inf
        action = (-1,-1)
        #check if done
        if not not stateOfTheBoard.whoWon() or not stateOfTheBoard.turn < maxRoundDepth:
            return stateOfTheBoard.evaluateState(), action

       
        for chosenFigure in range(0,len(stateOfTheBoard.figures[self.team])):
            for chosenMove in range(0,len(stateOfTheBoard.actionMoves)):
                b = StateOfTheBoard(shape = stateOfTheBoard.shape, turn = stateOfTheBoard.turn, board = stateOfTheBoard.board, figures = stateOfTheBoard.figures)
                legal = b.step(self.team, chosenFigure, ACTION_MOVE, chosenMove)
                if legal[0]:#checks if the b.step was actually a legal action/move
                    b.update()
                    #print('depth')
                    
                    #print(b.turn)
                    score = self._min(b, alpha, beta, depth+1, maxRoundDepth)[0]
                    if score > max_value:
                        max_value = score
                        action = (chosenFigure, chosenMove)
                        if max_value == self.winValue:
                            self.cache[board_hash] = max_value, action
                            return max_value, action
                    if max_value >= beta:
                        self.cache[board_hash] = max_value, action
                        return max_value, action
                    alpha = max(alpha, max_value)
        self.cache[board_hash] = max_value, action
        return max_value, action


    def _min(self, stateOfTheBoard: StateOfTheBoard, alpha, beta, depth, maxRoundDepth):
        
         #check if hashed
        board_hash = stateOfTheBoard.hashValue()
        if board_hash in self.cache:
            return self.cache[board_hash]
        
        min_value = math.inf
        action =  (-1,-1)
        #check if done
        if not not stateOfTheBoard.whoWon() or not stateOfTheBoard.turn < maxRoundDepth:
            return stateOfTheBoard.evaluateState(), action

        for chosenFigure in range(0,len(stateOfTheBoard.figures[self._flipTeam(self.team)])):
            for chosenMove in range(0,len(stateOfTheBoard.actionMoves)):
                b = StateOfTheBoard(stateOfTheBoard.shape, stateOfTheBoard.turn, stateOfTheBoard.board, stateOfTheBoard.figures)
                legal = b.step(self._flipTeam(self.team), chosenFigure, ACTION_MOVE, chosenMove)
                if legal[0]:
                    score = self._max(b, alpha, beta, depth+1, maxRoundDepth)[0]
                    if score < min_value:
                        min_value = score
                        action = (chosenFigure, chosenMove)
                        if min_value == self.lossValue:
                            self.cache[board_hash] = min_value, action
                            return min_value, action
                    if min_value <= alpha:
                        self.cache[board_hash] = min_value, action
                        return min_value, action
                    beta = min(beta, min_value)
        self.cache[board_hash] = min_value, action
        return min_value, action

    def selectAction(self, stateOfTheBoard, steps_done):
        #alpha beta search with deepening
        startTime = time.time()
        val = -1
        bestAction = (-1,-1)
        
        #(score, action) = self._max(stateOfTheBoard, -math.inf, math.inf, 0, 3)

        for currentDepth in range(1, self.maxDepth):

            if time.time() - startTime > self.maxSearchtime: break
            
            (score, action) = self._max(stateOfTheBoard, -math.inf, math.inf, 0, currentDepth)
            self.cache = {}
            
            if score == self.winValue: 
                bestAction = action
                break
            if score > val:
                val = score
                bestAction = action

            

        
        
        print('Score__' + str(score))
        steps_done += 1
        
        chosenFigure = bestAction[0]
        chosenAction = bestAction[1]
        return chosenFigure, ACTION_MOVE, chosenAction, steps_done
    