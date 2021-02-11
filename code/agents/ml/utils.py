import numpy as np


def entropy(values: list) -> float:
    probs = [i[0][0] for i in values]
    res = [ele for ele in probs if ele > 0]

    if len(res) > 1:
        norm = [float(i) / sum(res) for i in res]
        return -(norm * np.log(norm) / np.log(len(res))).sum()
    else:
        return 0.0
