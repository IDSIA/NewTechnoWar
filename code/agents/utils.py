from math import log

import numpy as np


def entropy(values: list) -> float:
    """
    :param values:  a list of probabilities-like values
    :return: the entropy value of the given list of values
    """
    n = len(values)
    if n <= 1:
        return 0.0

    m = min(values)
    values = [v + m for v in values]

    s = sum(values)
    if s == 0:
        return 0.0

    # normalize [0,1]
    values = [v / s for v in values]

    h = -sum(v * log(v) for v in values if v > 0)

    entr = h / log(n)

    entropy = 0 if entr < 0 else entr

    # entropy = 1 if entr > 1 else 0 if entr < 0 else entr

    return entropy


def standardD(values: list) -> float:
    return np.std(values)
