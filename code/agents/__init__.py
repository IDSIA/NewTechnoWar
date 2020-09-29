__all__ = [
    'MatchManager', 'buildMatchManager',
    'Agent', 'Human',
    'GreedyAgent', 'AlphaBetaAgent', 'RandomAgent'
]

from agents.interface import Agent
from agents.adversarial.dummy import RandomAgent
from agents.matchmanager import MatchManager, buildMatchManager
from agents.interactive.interactive import Human
from agents.adversarial.greedy import GreedyAgent
from agents.adversarial.alphabeta import AlphaBetaAgent
