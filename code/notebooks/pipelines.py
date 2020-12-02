from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer

from sklearn.ensemble import RandomForestClassifier
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
import joblib


def pipelineClassifier(df, name):
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
                               ('classifier', classifier)])
        pipe.fit(X, y)
        file_name = f'{name}_{classifier.__class__.__name__}.joblib'
        joblib.dump(pipe, file_name)


def pipelineRegressor(df, name, color):
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
                               ('regressor', regressor)])
        pipe.fit(X, y)
        file_name = f'{name}_{regressor.__class__.__name__}_{color}.joblib'
        joblib.dump(pipe, file_name)


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


def dfRegressor(dataframes, pilots):
    for p in pilots:
        df = pd.read_pickle(dataframes[p])
        df = df.loc[(((df.meta_p_red == "GreedyAgent") & (df.meta_p_blue == "GreedyAgent")) | (
                (df.meta_p_red == "GreedyAgent") & (df.meta_p_blue == "RandomAgent")) | (
                             (df.meta_p_red == "RandomAgent") & (df.meta_p_blue == "GreedyAgent")))]
        df_red = dfColor(df, "red")
        df_blue = dfColor(df, "blue")
        pipelineRegressor(df_red, p, "red")
        pipelineRegressor(df_blue, p, "blue")


if __name__ == '__main__':
    dataframes = {"Junction": "../../../data.scenarioJunction.pkl.gz",
                  "JunctionExo": "../../../data.scenarioJunctionExo.pkl.gz",
                  "Test1v1": "../../../data.2020-11-09.scenarioTest1v1.pkl.gz",
                  "Test2v2": "../../../data.2020-11-09.scenarioTest2v2.pkl.gz"}
    # pilots = ["BridgeHead", "CrossingTheCity", "Junction", "JunctionExo", "Roadblock", "Test1v1", "Test2v2"]
    pilots = ["JunctionExo"]

    #dfClassifier(dataframes, pilots)
    dfRegressor(dataframes, pilots)
