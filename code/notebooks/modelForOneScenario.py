import sys

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier


def regressor(df_red, df_blue, scenario, out):
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

        joblib.dump(rfr_red, out + f'{scenario}_{regressor.__class__.__name__}_red.joblib')
        joblib.dump(rfr_blue, out + f'{scenario}_{regressor.__class__.__name__}_blue.joblib')
        joblib.dump(rfr, out + f'{scenario}_{regressor.__class__.__name__}.joblib')


def classifier(df_red, df_blue, scenario, out):
    X_red = df_red.drop(['winner', 'label'], axis=1)
    y_red = df_red['label']

    X_blue = df_blue.drop(['winner', 'label'], axis=1)
    y_blue = df_blue['label']

    X = pd.concat([X_red, X_blue])
    y = pd.concat([y_red, y_blue])
    classifiers = [
        RandomForestClassifier(),
    ]  # in questo modo posso utilizzare altri regressori diversi dal RandomForest
    for c in classifiers:
        rfr_red = c.fit(X_red, y_red)
        rfr_blue = c.fit(X_blue, y_blue)
        rfr = c.fit(X, y)

        joblib.dump(rfr_red, out + f'{scenario}_{c.__class__.__name__}_red.joblib')
        joblib.dump(rfr_blue, out + f'{scenario}_{c.__class__.__name__}_blue.joblib')
        joblib.dump(rfr, out + f'{scenario}_{c.__class__.__name__}.joblib')


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

    scenario = sys.argv[1]
    fn = sys.argv[2]
    out = sys.argv[3]
    df = pd.read_pickle(fn)
    df_red, df_blue = splitDf(df)
    classifier(df_red, df_blue, scenario, out)
    regressor(df_red, df_blue, scenario, out)
