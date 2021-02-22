import logging.config
import math
import os
import random
import uuid
from datetime import datetime
from multiprocessing import Pool, cpu_count

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

from agents import MatchManager, GreedyAgent, ClassifierAgent, RegressionAgent, RandomAgent, Agent
from core.const import RED, BLUE
from core.game import vectorStateInfo, vectorState
from core.vectors import vectorActionInfo, vectorAction, vectorBoardInfo, vectorBoard
from scenarios import scenarioJunction
from utils.setup_logging import setup_logging

ALL = 'all'
CORES = cpu_count()
ELO_POINTS = 400
ELO_K = 40

logger = logging.getLogger("tourney")


class Player:

    def __init__(self, kind: str = '', var='', filename: str = '', points: int = ELO_POINTS):
        self.id = str(uuid.uuid4())
        self.kind = kind
        self.var = var
        self.filename = filename
        self.points = points
        self.wins = 0
        self.losses = 0

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

    def agent(self, team, seed) -> Agent:
        if self.kind == 'gre':
            return GreedyAgent(team, seed=seed)
        if self.kind == 'cls':
            return ClassifierAgent(team, self.filename, seed=seed)
        if self.kind == 'reg':
            return RegressionAgent(team, self.filename, seed=seed)

        return RandomAgent(team)


class Population:

    def __init__(self, size: int = 20, team: str = None, top_n: int = 5, kind: str = '', filename: str = ''):
        self.id = str(uuid.uuid4())

        self.team = team
        self.size = size
        self.count = size
        self.top_n = top_n

        self.kind = kind
        self.filename = filename

        self.population = [Player(kind, team, filename) for _ in range(size)]

        self.i = 0

        self.df = None

    def __repr__(self):
        return f'[{self.team} ({self.top_n}/{self.size}): {self.kind} {self.team}]'

    def __str__(self):
        return self.__repr__()

    def reset(self) -> None:
        random.shuffle(self.population)
        self.i = 0

    def next(self) -> Player or None:
        p = self.population[self.i]
        self.i = (self.i + 1) % self.size
        return p

    def ladder(self, raw: pd.DataFrame) -> None:
        self.population = sorted(self.population, key=lambda x: -x.points)

        logger.info(f'{self}: Ladder TOP 10')
        for i in range(self.size):
            pop = self.population[i]
            logger.info(
                f'{self}: ({i + 1:2}) {pop.kind:5} {pop.id:5}: {pop.points:6.2f} (W: {pop.wins:3} L: {pop.losses:3})'
            )
        logger.info(f'{self}: top {self.top_n} ')

        top_ids = [p.id for p in self.population[:self.top_n]]

        # create new dataframes
        df = raw[raw['meta_player'].isin(top_ids)] \
            .drop(['meta_seed', 'meta_scenario', 'meta_player', 'action_team'], axis=1, errors='ignore') \
            .dropna(axis=1, how='all')

        if df.shape == (0, 0):
            return

        df['label'] = df['winner'].apply(lambda x: 1 if x == self.team else -1)

        if self.df:
            self.df = pd.concat([self.df, df])
        else:
            self.df = df

    def trainArgs(self, epoch, DIR_MODELS) -> tuple:
        if self.df is None:
            return self.id, epoch, None, None, self.team, self.kind, self.team, DIR_MODELS

        X = self.df.drop(['winner', 'label'], axis=1, errors='ignore')
        y = self.df['label']

        logger.debug(f'{self}: shapes X={X.shape} y={y.shape}')

        return self.id, epoch, X, y, self.team, self.kind, self.team, DIR_MODELS

    def setup(self, filename: str = ''):
        if self.kind == 'gre':
            return

        logger.debug(f'{self}: setup with {filename}')
        self.population = [Player(self.kind, self.team, filename) for _ in range(self.size)]

    def evolve(self, filename: str = ''):
        if self.kind == 'gre':
            return

        self.population = sorted(self.population, key=lambda x: -x.points)

        self.population = self.population[:self.top_n] + [
            Player(self.kind, self.team, filename) for _ in range(self.size - self.top_n)
        ]


def playJunction(seed: int, red: Player, blue: Player) -> MatchManager:
    """
    Start a game with the given configuration on the 'Junction' scenario.
    @param seed: random seed to use
    @param red:  red Player
    @param blue: blue Player
    @return: a MatchManger object with all the stored results from the match
    """
    board, state = scenarioJunction()

    playerRed = red.agent(RED, seed)
    playerBlue = blue.agent(BLUE, seed)

    logger.debug(f'match between:\n' +
                 f'\t{playerRed.team:5}: {red.id:5} ({red.kind} {red.var}) -> {playerRed.__class__.__name__}\n' +
                 f'\t{playerBlue.team:5}: {blue.id:5} ({blue.kind} {red.var}) -> {playerBlue.__class__.__name__}')

    mm = MatchManager(' ', playerRed, playerBlue, board, state, seed=seed)
    while not mm.end:
        mm.nextStep()

    return mm


def play(args) -> tuple:
    red: Player = args[0]
    blue: Player = args[1]
    seed: int = args[2]
    epoch: int = args[3]
    dir_data: str = args[4]

    mm = playJunction(seed, red, blue)

    # get data frames
    states_cols = vectorStateInfo()
    states_data = [vectorState(x) for x in mm.states_history]
    df_state = pd.DataFrame(columns=states_cols, data=states_data)

    actions_cols = vectorActionInfo()
    actions_data = [vectorAction(x) for x in mm.actions_history]
    df_action = pd.DataFrame(columns=actions_cols, data=actions_data)

    board_cols = vectorBoardInfo()
    board_data = [vectorBoard(mm.board, s, a) for s, a in zip(mm.states_history, mm.actions_history)]
    df_board = pd.DataFrame(columns=board_cols, data=board_data)

    df = pd.concat([df_state, df_action, df_board], axis=1)

    df['winner'] = mm.winner
    df['meta_player'] = df['action_team'].apply(lambda x: red.id if x == RED else blue.id)

    # save to disk
    filename = f'game.{epoch}.{seed}.{red.id}.{blue.id}.pkl.gz'
    df.to_pickle(os.path.join(dir_data, str(epoch), filename), compression='gzip')

    return red.id, blue.id, mm.winner


def compress(epoch: int, dir_data) -> pd.DataFrame:
    df_dir = os.path.join(dir_data, str(epoch))
    files = [f for f in os.listdir(df_dir)]

    dfs = [
        pd.concat([
            pd.read_pickle(os.path.join(df_dir, f), compression='gzip') for f in files[i:i + 1000]
        ]) for i in range(0, len(files), 1000)
    ]

    dfs = pd.concat(dfs)

    dfs.to_pickle(os.path.join(dir_data, f'df.{epoch}.pkl.gz'), compression='gzip')

    return dfs


def initBuildDataFrame(raw: pd.DataFrame) -> tuple:
    df = raw.drop(['meta_scenario', 'meta_seed', 'meta_player'], axis=1, errors='ignore').dropna(axis=1, how='all')

    df_red = df[df['action_team'] == 'red'].copy().drop('action_team', axis=1, errors='ignore')
    df_blue = df[df['action_team'] == 'blue'].copy().drop('action_team', axis=1, errors='ignore')

    df_red['label'] = df_red['winner'].apply(lambda x: 1 if x == 'red' else -1)
    df_blue['label'] = df_blue['winner'].apply(lambda x: 1 if x == 'blue' else -1)

    X_red = df_red.drop(['winner', 'label'], axis=1, errors='ignore')
    y_red = df_red['label']

    X_blue = df_blue.drop(['winner', 'label'], axis=1, errors='ignore')
    y_blue = df_blue['label']

    logger.debug(f'shapes: X_red={X_red.shape} y_red={y_red.shape} X_blue={X_blue.shape} y_blue{y_blue.shape}')

    return X_red, y_red, X_blue, y_blue


def buildModel(args) -> tuple:
    pid, epoch, X, y, team, kind, var, dir_models = args

    if X is None or y is None:
        return pid, None

    if kind == 'cls':
        m = RandomForestClassifier()
    elif kind == 'reg':
        m = RandomForestRegressor()
    else:
        return pid, ''

    m.fit(X, y)

    filename = os.path.join(dir_models, f'{epoch}_{pid}_{team}_{kind}_{var}.joblib')
    joblib.dump(m, filename)

    logger.info(f'built for {pid} ({team} {kind} {var}): {filename}')

    return pid, filename


def main() -> None:
    # setup folders
    TODAY = datetime.now().strftime("%Y%m%d-%H%M%S")
    DIR_WORK = os.path.join('tournament', TODAY)
    DIR_MODELS = os.path.join(DIR_WORK, "models")
    DIR_DATA = os.path.join(DIR_WORK, "data")
    DIR_OUT = os.path.join(DIR_WORK, "out")

    seed = 20210217
    size = 20  # TODO: add a distribution parameter
    top_models = 5
    turns_per_epoch = 10
    games_per_turn = 10
    epochs = 5

    random.seed = seed

    # TODO: we need a different population for CLSs, REGs, and GREs based on color red, blue, or both (total: 9 pops!)
    pops = {
        RED: [
            Population(size=size, top_n=top_models, kind='cls', team=RED),
            Population(size=size, top_n=top_models, kind='reg', team=RED),
            Population(size=size, top_n=top_models, kind='gre', team=RED),
        ],
        BLUE: [
            Population(size=size, top_n=top_models, kind='cls', team=BLUE),
            Population(size=size, top_n=top_models, kind='reg', team=BLUE),
            Population(size=size, top_n=top_models, kind='gre', team=BLUE),
        ],
        ALL: [
            # TODO: this need to be thought better
            #     Population(size=size, top_n=top_models, kind='cls', team=ALL),
            #     Population(size=size, top_n=top_models, kind='reg', team=ALL),
            Population(size=size, top_n=top_models, kind='gre', team=ALL)
        ]
    }

    # initial population TODO: put this in a generator function
    populations = {}
    for pop in pops.values():
        for p in pop:
            populations[p.id] = p

    with Pool(CORES, maxtasksperchild=1) as pool:
        for epoch in range(epochs):
            logger.info(f"EPOCH: {epoch}")

            # create folders for this epoc
            os.makedirs(os.path.join(DIR_DATA, str(epoch)), exist_ok=True)
            os.makedirs(os.path.join(DIR_MODELS, str(epoch)), exist_ok=True)
            os.makedirs(os.path.join(DIR_OUT, str(epoch)), exist_ok=True)

            # collect all player ids
            players = {}
            for pop in pops.values():
                for p in pop:
                    for e in p.population:
                        players[e.id] = e

            # play with all other players
            logger.info('Playing games...')
            for i in range(turns_per_epoch):
                # reset population internal distributions
                for pop in pops.values():
                    for p in pop:
                        p.reset()

                args = []
                for j in range(games_per_turn):
                    if epoch == 0:
                        red_pop = random.choice(pops[ALL])
                        blue_pop = random.choice(pops[ALL])
                    else:
                        # for each game, choose a red from all the reds...
                        red_pop = random.choice(pops[RED] + pops[ALL])
                        # ...and a blue from all the blues
                        blue_pop = random.choice(pops[BLUE] + pops[ALL])

                    args.append(
                        (red_pop.next(), blue_pop.next(), random.randint(100000000, 999999999), epoch, DIR_DATA)
                    )

                results = pool.map(play, args)

                logger.info('update results:')
                for rid, bid, winner in results:
                    logger.info(f'\t* RED={rid} vs BLUE={bid}: {winner} wins!')
                    red = players[rid]
                    blue = players[bid]
                    if winner == RED:
                        red.win(blue)
                    else:
                        blue.win(red)

            # collect generated data
            df = compress(epoch, DIR_DATA)

            logger.info('building models...')
            args = []

            if epoch == 0:
                logger.info('first build of models')
                X_red, y_red, X_blue, y_blue = initBuildDataFrame(df)

                for k, pop in populations.items():
                    if pop.team == RED:
                        args.append((k, epoch, X_red, y_red, RED, pop.kind, RED, DIR_MODELS))
                    else:
                        args.append((k, epoch, X_blue, y_blue, BLUE, pop.kind, BLUE, DIR_MODELS))

            else:
                logger.info('choosing best models...')
                for pop in pops.values():
                    for p in pop:
                        p.ladder(df.copy())
                        args.append(p.trainArgs(epoch, DIR_MODELS))

            # parallel build models based on dataframes built above
            models = pool.map(buildModel, args)

            for pid, model in models:
                if epoch == 0:
                    populations[pid].setup(model)
                else:
                    populations[pid].evolve(model)


if __name__ == '__main__':
    setup_logging()
    main()
