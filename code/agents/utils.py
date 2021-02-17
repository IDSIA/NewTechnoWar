from math import log


def entropy(values: list) -> float:
    n = len(values)
    if n <= 1:
        return 0.0
    
    m = min(values)
    values = [v+m for v in values]
    
    s = sum(values)
    if s == 0:
        return 0.0
    
    # normalize [0,1]
    values = [v/s for v in values]
    
    h = -sum(v * log(v) for v in values if v > 0)
    
    return h/log(n)
