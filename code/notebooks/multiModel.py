import sys

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier


def regressor(df_red, df_blue, scenario, out):
    X_red_move = df_red_move.drop(['winner', 'label'], axis=1)
    y_red_move = df_red_move['label']

    X_blue_move = df_blue_move.drop(['winner', 'label'], axis=1)
    y_blue_move = df_blue_move['label']

    X_red_attack = df_red_attack.drop(['winner', 'label'], axis=1)
    y_red_attack = df_red_attack['label']

    X_blue_attack = df_blue_attack.drop(['winner', 'label'], axis=1)
    y_blue_attack = df_blue_attack['label']

    X_red_pass = df_red_pass.drop(['winner', 'label'], axis=1)
    y_red_pass = df_red_pass['label']

    X_blue_pass = df_blue_pass.drop(['winner', 'label'], axis=1)
    y_blue_pass = df_blue_pass['label']

    X = pd.concat([X_red_move, X_blue_move, X_red_attack, X_blue_attack, X_red_pass, X_blue_pass])
    y = pd.concat([y_red_move, y_blue_move, y_red_attack, y_blue_attack, y_red_pass, y_blue_pass])
    regressors = [
        RandomForestRegressor(),
    ]  # in questo modo posso utilizzare altri regressori diversi dal RandomForest
    for regressor in regressors:
        rfr_red_move = regressor.fit(X_red_move, y_red_move)
        rfr_red_attack = regressor.fit(X_red_attack, y_red_attack)
        rfr_red_pass = regressor.fit(X_red_pass, y_red_pass)

        rfr_blue_move = regressor.fit(X_blue_move, y_blue_move)
        rfr_blue_attack = regressor.fit(X_blue_attack, y_blue_attack)
        rfr_blue_pass = regressor.fit(X_blue_pass, y_blue_pass)

        rfr = regressor.fit(X, y)

        joblib.dump(rfr_red_move, out + f'{scenario}_{regressor.__class__.__name__}_red_move.joblib')
        joblib.dump(rfr_red_attack, out + f'{scenario}_{regressor.__class__.__name__}_red_attack.joblib')
        joblib.dump(rfr_red_pass, out + f'{scenario}_{regressor.__class__.__name__}_red_pass.joblib')

        joblib.dump(rfr_blue_move, out + f'{scenario}_{regressor.__class__.__name__}_blue_move.joblib')
        joblib.dump(rfr_blue_attack, out + f'{scenario}_{regressor.__class__.__name__}_blue_attack.joblib')
        joblib.dump(rfr_blue_pass, out + f'{scenario}_{regressor.__class__.__name__}_blue_pass.joblib')

        joblib.dump(rfr, out + f'{scenario}_{regressor.__class__.__name__}.joblib')

def classifier(df_red, df_blue, scenario, out):
    X_red_move = df_red_move.drop(['winner', 'label'], axis=1)
    y_red_move = df_red_move['label']

    X_blue_move = df_blue_move.drop(['winner', 'label'], axis=1)
    y_blue_move = df_blue_move['label']

    X_red_attack = df_red_attack.drop(['winner', 'label'], axis=1)
    y_red_attack = df_red_attack['label']

    X_blue_attack = df_blue_attack.drop(['winner', 'label'], axis=1)
    y_blue_attack = df_blue_attack['label']

    X_red_pass = df_red_pass.drop(['winner', 'label'], axis=1)
    y_red_pass = df_red_pass['label']

    X_blue_pass = df_blue_pass.drop(['winner', 'label'], axis=1)
    y_blue_pass = df_blue_pass['label']

    X = pd.concat([X_red_move, X_blue_move, X_red_attack, X_blue_attack, X_red_pass, X_blue_pass])
    y = pd.concat([y_red_move, y_blue_move, y_red_attack, y_blue_attack, y_red_pass, y_blue_pass])

    classifiers = [
        RandomForestClassifier(),
    ]  # in questo modo posso utilizzare altri regressori diversi dal RandomForest
    for c in classifiers:
        rfr_red_move = c.fit(X_red_move, y_red_move)
        rfr_red_attack = c.fit(X_red_attack, y_red_attack)
        rfr_red_pass = c.fit(X_red_pass, y_red_pass)

        rfr_blue_move = c.fit(X_blue_move, y_blue_move)
        rfr_blue_attack = c.fit(X_blue_attack, y_blue_attack)
        rfr_blue_pass = c.fit(X_blue_pass, y_blue_pass)

        rfr = c.fit(X, y)

        joblib.dump(rfr_red_move, out + f'{scenario}_{c.__class__.__name__}_red_move.joblib')
        joblib.dump(rfr_red_attack, out + f'{scenario}_{c.__class__.__name__}_red_attack.joblib')
        joblib.dump(rfr_red_pass, out + f'{scenario}_{c.__class__.__name__}_red_pass.joblib')

        joblib.dump(rfr_blue_move, out + f'{scenario}_{c.__class__.__name__}_blue_move.joblib')
        joblib.dump(rfr_blue_attack, out + f'{scenario}_{c.__class__.__name__}_blue_attack.joblib')
        joblib.dump(rfr_blue_pass, out + f'{scenario}_{c.__class__.__name__}_blue_pass.joblib')

        joblib.dump(rfr, out + f'{scenario}_{c.__class__.__name__}.joblib')


def splitDf(df):
    df.drop(['meta_scenario', 'meta_p_red', 'meta_p_blue', 'meta_seed'], axis=1, errors="ignore", inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

    df_red = df[df['action_team'] == 'red'].copy().drop('action_team', axis=1)
    df_blue = df[df['action_team'] == 'blue'].copy().drop('action_team', axis=1)

    df_red['label'] = df_red['winner'].apply(lambda x: 1 if x == 'red' else -1)
    df_blue['label'] = df_blue['winner'].apply(lambda x: 1 if x == 'blue' else -1)

    df_red_move = df_red.loc[((df_red['action_type_Move'] == True) | (df_red['action_type_LoadInto'] == True))].copy()
    df_red_attack = df_red.loc[(
            (df_red['action_type_Attack'] == True) | (df_red['action_type_AttackGround'] == True) | (
            df_red['action_type_AttackRespond'] == True))].copy()
    df_red_pass = df_red.loc[((df_red['action_type_Pass'] == True) | (df_red['action_type_PassFigure'] == True) | (
            df_red['action_type_PassTeam'] == True) | (df_red['action_type_PassRespond'] == True))].copy()

    df_blue_move = df_blue.loc[
        ((df_blue['action_type_Move'] == True) | (df_blue['action_type_LoadInto'] == True))].copy()
    df_blue_attack = df_blue.loc[(
            (df_blue['action_type_Attack'] == True) | (df_blue['action_type_AttackGround'] == True) | (
            df_blue['action_type_AttackRespond'] == True))].copy()
    df_blue_pass = df_blue.loc[((df_blue['action_type_Pass'] == True) | (df_blue['action_type_PassFigure'] == True) | (
            df_blue['action_type_PassTeam'] == True) | (df_blue['action_type_PassRespond'] == True))].copy()

    return df_red_move, df_blue_move, df_red_attack, df_blue_attack, df_red_pass, df_blue_pass


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('no arguments passed')
        sys.exit()

    scenario = sys.argv[1]
    fn = sys.argv[2]
    out = sys.argv[3]
    df = pd.read_pickle(fn)
    df_red_move, df_blue_move, df_red_attack, df_blue_attack, df_red_pass, df_blue_pass = splitDf(df)
    classifier(df_red_move, df_blue_move, df_red_attack, df_blue_attack, df_red_pass, df_blue_pass, scenario, out)
    regressor(df_red_move, df_blue_move, df_red_attack, df_blue_attack, df_red_pass, df_blue_pass, scenario, out)
