import numpy as np


def entropy(values: list) -> float:
    values = [v for v in values if v >= 0]
    if len(values) > 1 and sum(values) > 0:
        norm = [float(i) / sum(values) for i in values]
        return -(norm * np.log(norm)).sum() / np.log(len(values))
    else:
        return 0.0
