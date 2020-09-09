import _pickle as cpickle


def deepcopy(obj):
    return cpickle.loads(cpickle.dumps(obj, -1))
