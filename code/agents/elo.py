import uuid
import math

from torch import IntStorage

from agents.interface import Agent

ELO_POINTS: float = 400.0
ELO_K: float = 40.0


class ELO:

    def __init__(self, builder, team: str, name: str = '', points: float = ELO_POINTS):
        """
        'builder' is a function f(team, seed) that returns an object that implement the interface Agent.
        """
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.team: str = team

        self.points: float = points

        self.wins: int = 0
        self.losses: int = 0

        self.builder = builder

    def games(self) -> int:
        return self.wins + self.losses

    def expected(self, other):
        return 1. / (1. + math.pow(10., (other.points - self.points) / ELO_POINTS))

    def update(self, points, exp):
        self.points = self.points + ELO_K * (points - exp)

    def win(self, against):
        self.wins += 1
        against.losses += 1

        eA = self.expected(against)
        eB = against.expected(self)

        self.update(1, eA)
        against.update(0, eB)

    def agent(self, seed) -> Agent:
        return self.builder(self.team, seed)

    def __repr__(self) -> str:
        return f'{self.name} {self.points} [W:{self.wins}, L:{self.losses}]'

    def __str__(self) -> str:
        return f'{self.name} {self.points} [W:{self.wins}, L:{self.losses}]'

    def __lt__(self, other):
        return self.points < other.points

    def __eq__(self, other: object) -> bool:
        if not other:
            return False
        if not isinstance(other, ELO):
            return False

        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
