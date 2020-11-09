from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
import pandas as pd
from sklearn.naive_bayes import GaussianNB
#import os.path as op

import joblib
#dir_path = op.dirname(op.realpath(__file__))


def pipelineClassifier(df, name):
    X = df.drop(['winner', 'meta_scenario', 'meta_p_red', 'meta_p_blue', 'meta_seed'], axis=1, errors="ignore")
    y = df['winner']
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore'))])
    c = df.select_dtypes(include=['object']).drop(['winner', 'meta_scenario', 'meta_p_red', 'meta_p_blue', 'meta_seed'],
                                                  axis=1, errors="ignore").columns
    preprocessor = ColumnTransformer(transformers=[('cat', categorical_transformer, c)])
    classifiers = [
        #KNeighborsClassifier(3),
        # SVC(kernel="rbf", C=0.025, probability=True),
        # NuSVC(probability=True),
        #DecisionTreeClassifier(),
        RandomForestClassifier(),
        #AdaBoostClassifier(),
        #GradientBoostingClassifier(),
        #GaussianNB(),
    ]
    for classifier in classifiers:
        pipe = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', classifier)])
        pipe.fit(X, y)
        file_name = f'{name}_{classifier.__class__.__name__}.joblib'
        joblib.dump(pipe, file_name)


if __name__ == '__main__':
    dataframes = {"Junction": "../../../data.2020-11-09.scenarioJunction.pkl.gz",
                  "JunctionExo": "../../../data.2020-11-09.scenarioJunctionExo.pkl.gz",
                  "Test1v1": "../../../data.2020-11-09.scenarioTest1v1.pkl.gz",
                  "Test2v2": "../../../data.2020-11-09.scenarioTest2v2.pkl.gz"}
    # pilots = ["BridgeHead", "CrossingTheCity", "Junction", "JunctionExo", "Roadblock", "Test1v1", "Test2v2"]
    pilots = ["Junction", "JunctionExo", "Test1v1", "Test2v2"]

    for p in pilots:
        df = pd.read_pickle(dataframes[p])
        '''df = df.loc[(((df.meta_p_red == "GreedyAgent") & (df.meta_p_blue == "GreedyAgent")) | (
                    (df.meta_p_red == "GreedyAgent") & (df.meta_p_blue == "RandomAgent")) | (
                                 (df.meta_p_red == "RandomAgent") & (df.meta_p_blue == "GreedyAgent")))]'''

        pipelineClassifier(df, p)
