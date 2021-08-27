

class dotdict(dict):
    def __getattr__(self, name):
        if name == '__getstate__':
            return super.__getstate__()
        return self[name]
