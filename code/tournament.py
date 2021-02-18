import logging.config
import math
import os
import random
from datetime import datetime
from multiprocessing import Pool, cpu_count

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

from agents import MatchManager, GreedyAgent, ClassifierAgent, RegressionAgent, RandomAgent, Agent
from core.const import RED, BLUE
from core.game.state import vectorStateInfo, vectorState, vectorActionInfo, vectorAction
from scenarios import scenarioJunction
from utils.setup_logging import setup_logging

CORES = cpu_count()
ELO_POINTS = 400
ELO_K = 40

logger = logging.getLogger("tourney")


class Player:

    def __init__(self, id: int = 0, kind: str = '', var='', filename: str = '', points: int = ELO_POINTS):
        self.id = id
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

    df = pd.concat([df_state, df_action], axis=1)

    df['winner'] = mm.winner
    df['meta_i_red'] = red.id
    df['meta_i_blue'] = blue.id

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


def splitDataFrame(df: pd.DataFrame) -> tuple:
    df = df.dropna(axis=1, how='all')

    df_red = df[df['action_team'] == 'red'].copy().drop('action_team', axis=1, errors='ignore')
    df_blue = df[df['action_team'] == 'blue'].copy().drop('action_team', axis=1, errors='ignore')

    df_red['label'] = df_red['winner'].apply(lambda x: 1 if x == 'red' else -1)
    df_blue['label'] = df_blue['winner'].apply(lambda x: 1 if x == 'blue' else -1)

    X_red = df_red.drop(['winner', 'label'], axis=1, errors='ignore')
    y_red = df_red['label']

    X_blue = df_blue.drop(['winner', 'label'], axis=1, errors='ignore')
    y_blue = df_blue['label']

    X = pd.concat([X_red, X_blue])
    y = pd.concat([y_red, y_blue])

    logger.debug(f'shapes: X={X.shape} y={y.shape} X_red={X_red.shape} y_red={y_red.shape} ' +
                 f'X_blue={X_blue.shape} y_blue{y_blue.shape}')

    return X, y, X_red, y_red, X_blue, y_blue


def initBuildDataFrame(raw: pd.DataFrame) -> tuple:
    df = raw.drop([
        'meta_scenario', 'meta_seed', 'meta_i_red', 'meta_i_blue'
    ], axis=1, errors='ignore')

    return splitDataFrame(df)


def buildDataFrame(raw: pd.DataFrame, ids: list) -> tuple:
    df = raw[raw['meta_i_red'].isin(ids) | raw['meta_i_blue'].isin(ids)].drop([
        'meta_seed', 'meta_scenario', 'meta_i_red', 'meta_i_blue'
    ], axis=1, errors='ignore')

    return splitDataFrame(df)


def buildModel(args) -> tuple:
    epoch, m, X, y, s, t, dir_models = args

    m.fit(X, y)

    filename = os.path.join(dir_models, f'{epoch}_{s}_{t}.joblib')
    joblib.dump(m, filename)

    logger.info(f'built ({s} {t}): {filename}')

    return s, t, filename


def main() -> None:
    # setup folders
    TODAY = datetime.now().strftime("%Y%m%d-%H%M%S")
    DIR_WORK = os.path.join('tournament', TODAY)
    DIR_MODELS = os.path.join(DIR_WORK, "models")
    DIR_DATA = os.path.join(DIR_WORK, "data")
    DIR_OUT = os.path.join(DIR_WORK, "out")

    seed = 20210217
    size = 20
    count = size
    games_per_epoch = 10
    epochs = 5
    top_models = 2

    random.seed = seed

    population = [Player(c, 'gre') for c in range(count)]

    with Pool(CORES, maxtasksperchild=1) as p:
        for epoch in range(epochs):
            logger.info(f"EPOCH: {epoch}")

            os.makedirs(os.path.join(DIR_DATA, str(epoch)), exist_ok=True)
            os.makedirs(os.path.join(DIR_MODELS, str(epoch)), exist_ok=True)
            os.makedirs(os.path.join(DIR_OUT, str(epoch)), exist_ok=True)

            # play with all other players
            logger.info('Playing games...')
            for _ in range(games_per_epoch):
                # randomly select a pair of players
                random.shuffle(population)
                args = []
                for i in range(0, len(population), 2):
                    args.append(
                        (population[i], population[i + 1], random.randint(100000000, 999999999), epoch, DIR_DATA)
                    )
                results = p.map(play, args)
                players = {p.id: p for p in population}

                logger.info('update results:')
                for rid, bid, winner in results:
                    logger.info(f'\t* {rid:5} vs {bid:5}: {winner} wins!')
                    red = players[rid]
                    blue = players[bid]
                    if winner == RED:
                        red.win(blue)
                    else:
                        blue.win(red)

            # collect generated data
            df = compress(epoch, DIR_DATA)

            logger.info('building models...')
            if epoch == 0:
                logger.info('first build of models')
                X, y, X_red, y_red, X_blue, y_blue = initBuildDataFrame(df)

            else:
                logger.info('choosing best models...')
                population = sorted(population, key=lambda x: -x.points)
                top_ids = [p.id for p in population[:top_models]]

                logger.info('TOP 10:')
                for i in range(10):
                    pop = population[i]
                    logger.info(
                        f'({i + 1:2}) {pop.kind:5} {pop.id:5}: {pop.points:6.2f} (W: {pop.wins:3} L: {pop.losses:3})')
                logger.info('top ', top_models, 'will contribute with their data')

                X, y, X_red, y_red, X_blue, y_blue = buildDataFrame(df, top_ids)

            # build models based on built dataframes
            args = [
                (epoch, RandomForestRegressor(), X_red, y_red, 'reg', 'red', DIR_MODELS),
                (epoch, RandomForestRegressor(), X_blue, y_blue, 'reg', 'blue', DIR_MODELS),
                (epoch, RandomForestRegressor(), X, y, 'reg', 'all', DIR_MODELS),
                (epoch, RandomForestClassifier(), X_red, y_red, 'cls', 'red', DIR_MODELS),
                (epoch, RandomForestClassifier(), X_blue, y_blue, 'cls', 'blue', DIR_MODELS),
                (epoch, RandomForestClassifier(), X, y, 'cls', 'all', DIR_MODELS),
            ]

            models = p.map(buildModel, args)

            # add a default mix of players
            population = []
            for i in range(3):
                for s, t, filename in models:
                    logger.info(f'added: ({s} {t}): filename')
                    population.append(Player(count, s, t, filename))
                    count += 1
            for i in range(2):
                population.append(Player(count, 'gre'))
                count += 1


if __name__ == '__main__':
    setup_logging()
    main()
