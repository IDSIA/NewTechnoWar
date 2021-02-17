import sys

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier


def dfClassifier(dataframes, pilots):
    for p in pilots:
        df = pd.read_pickle(dataframes[p])
        df_red, df_blue = splitDf(df)

        X_red = df_red.drop(['winner', 'label'], axis=1)
        y_red = df_red['label']

        X_blue = df_blue.drop(['winner', 'label'], axis=1)
        y_blue = df_blue['label']

        X = pd.concat([X_red, X_blue])
        y = pd.concat([y_red, y_blue])
        classifiers = [
            RandomForestClassifier,
        ]  # in questo modo posso utilizzare altri regressori diversi dal RandomForest
        for c in classifiers:
            rfr_red = c.fit(X_red, y_red)
            rfr_blue = c.fit(X_blue, y_blue)
            rfr = c.fit(X, y)

            joblib.dump(rfr_red, out + f'{p}_{c.__class__.__name__}_red.joblib')
            joblib.dump(rfr_blue, out + f'{p}_{c.__class__.__name__}_blue.joblib')
            joblib.dump(rfr, out + f'{p}_{c.__class__.__name__}.joblib')


def dfRegressor(dataframes, pilots, out):
    for p in pilots:
        df = pd.read_pickle(dataframes[p])
        df_red, df_blue = splitDf(df)

        X_red = df_red.drop(['winner', 'label'], axis=1)
        y_red = df_red['label']

        X_blue = df_blue.drop(['winner', 'label'], axis=1)
        y_blue = df_blue['label']

        X = pd.concat([X_red, X_blue])
        y = pd.concat([y_red, y_blue])
        regressors = [
            RandomForestRegressor(),
        ]  # in questo modo posso utilizzare altri regressori diversi dal RandomForest
        for regressor in regressors:
            rfr_red = regressor.fit(X_red, y_red)
            rfr_blue = regressor.fit(X_blue, y_blue)
            rfr = regressor.fit(X, y)

            joblib.dump(rfr_red, out + f'{p}_{regressor.__class__.__name__}_red.joblib')
            joblib.dump(rfr_blue, out + f'{p}_{regressor.__class__.__name__}_blue.joblib')
            joblib.dump(rfr, out + f'{p}_{regressor.__class__.__name__}.joblib')


def splitDf(df):
    df.drop(['meta_scenario', 'meta_p_red', 'meta_p_blue', 'meta_seed'], axis=1, errors="ignore", inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    df_red = df[df['action_team'] == 'red'].copy().drop('action_team', axis=1)
    df_blue = df[df['action_team'] == 'blue'].copy().drop('action_team', axis=1)
    df_red['label'] = df_red['winner'].apply(lambda x: 1 if x == 'red' else -1)
    df_blue['label'] = df_blue['winner'].apply(lambda x: 1 if x == 'blue' else -1)
    return df_red, df_blue


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

    dfClassifier(dataframes, pilots, out)
    dfRegressor(dataframes, pilots, out)
