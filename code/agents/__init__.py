__all__ = [
    'MatchManager', 'buildMatchManager',
    'Agent', 'Human',
    'GreedyAgent', 'AlphaBetaAgent', 'RandomAgent', 'AlphaBetaFast1Agent',
    'ClassifierAgent', 'RegressionAgent', 'RegressionMultiAgent',
    'Puppet',
    'MCTSAgent',
    'ELOPlayer'
]

from agents.interface import Agent
from agents.matchmanager import MatchManager, buildMatchManager
from agents.interactive.interactive import Human
from agents.adversarial.dummy import RandomAgent
from agents.adversarial.greedy import GreedyAgent
from agents.adversarial.alphabeta import AlphaBetaAgent
from agents.adversarial.alphabetafast1 import AlphaBetaFast1Agent
from agents.adversarial.puppets import Puppet
from agents.ml.classifier import ClassifierAgent
from agents.ml.regression import RegressionAgent
from agents.ml.regressionMulti import RegressionMultiAgent
from agents.reinforced import MCTSAgent
from agents.elo import ELO
