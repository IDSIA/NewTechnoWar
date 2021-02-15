import sys

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def pipelineClassifier(df, name, out):
    X = df.drop(['winner', 'meta_scenario', 'meta_p_red', 'meta_p_blue', 'meta_seed'], axis=1, errors="ignore")
    y = df['winner']
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore'))])
    c = df.select_dtypes(include=['object']).drop(['winner', 'meta_scenario', 'meta_p_red', 'meta_p_blue', 'meta_seed'],
                                                  axis=1, errors="ignore").columns
    preprocessor = ColumnTransformer(transformers=[('cat', categorical_transformer, c)])
    classifiers = [
        RandomForestClassifier(),
    ]

    for classifier in classifiers:
        pipe = Pipeline(steps=[('preprocessor', preprocessor),
                               ('scale', StandardScaler()),
                               ('classifier', classifier)])
        pipe.fit(X, y)
        file_name = f'{name}_{classifier.__class__.__name__}.joblib'
        joblib.dump(pipe, out + file_name)


def pipelineRegressor(df, name, color, out):
    X = df.drop(['winner', 'meta_scenario', 'meta_p_red', 'meta_p_blue', 'meta_seed'], axis=1, errors="ignore")
    y = df['winner']
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore'))])
    c = df.select_dtypes(include=['object']).drop(['winner', 'meta_scenario', 'meta_p_red', 'meta_p_blue', 'meta_seed'],
                                                  axis=1, errors="ignore").columns
    preprocessor = ColumnTransformer(transformers=[('cat', categorical_transformer, c)])
    regressors = [
        RandomForestRegressor(n_estimators=1000, random_state=42),
    ]

    for regressor in regressors:
        pipe = Pipeline(steps=[('preprocessor', preprocessor),
                               ('scale', StandardScaler()),
                               ('regressor', regressor)])
        pipe.fit(X, y)
        file_name = f'{name}_{regressor.__class__.__name__}_{color}.joblib'
        joblib.dump(pipe, out + file_name)


def dfClassifier(dataframes, pilots):
    for p in pilots:
        df = pd.read_pickle(dataframes[p])
        df = df.loc[((df.meta_p_red == "GreedyAgent") & (df.meta_p_blue == "GreedyAgent"))]
        '''df = df.loc[(((df.meta_p_red == "GreedyAgent") & (df.meta_p_blue == "GreedyAgent")) | (
                    (df.meta_p_red == "GreedyAgent") & (df.meta_p_blue == "RandomAgent")) | (
                                 (df.meta_p_red == "RandomAgent") & (df.meta_p_blue == "GreedyAgent")))]'''

        pipelineClassifier(df, p)


def dfColor(df, color):
    df_new = pd.concat([df[[c for c in df.columns if color in c]], df['winner']], axis=1)
    df_new.loc[df.winner == color, "winner"] = +1
    df_new.loc[df.winner != color, "winner"] = -1
    return df_new


def dfRegressor(dataframes, pilots, out):
    for p in pilots:
        df = pd.read_pickle(dataframes[p])
        df = df.loc[(((df.meta_p_red == "GreedyAgent") & (df.meta_p_blue == "GreedyAgent")) | (
                (df.meta_p_red == "GreedyAgent") & (df.meta_p_blue == "RandomAgent")) | (
                             (df.meta_p_red == "RandomAgent") & (df.meta_p_blue == "GreedyAgent")))]
        df_red = dfColor(df, "red")
        df_blue = dfColor(df, "blue")
        pipelineRegressor(df_red, p, "red", out)
        pipelineRegressor(df_blue, p, "blue", out)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('no arguments passed')
        sys.exit()

    fn = sys.argv[1]
    out = sys.argv[2]

    dataframes = {"Junction": fn + "data.scenarioJunction.pkl.gz",
                  "JunctionExo": fn + "data.scenarioJunctionExo.pkl.gz",
                  "Test1v1": fn + "data.2020-11-09.scenarioTest1v1.pkl.gz",
                  "Test2v2": fn + "data.2020-11-09.scenarioTest2v2.pkl.gz"}
    # pilots = ["BridgeHead", "CrossingTheCity", "Junction", "JunctionExo", "Roadblock", "Test1v1", "Test2v2"]
    pilots = ["Junction"]

    # dfClassifier(dataframes, pilots)
    dfRegressor(dataframes, pilots, out)
