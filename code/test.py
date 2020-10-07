class A:
    def __init__(self, a, **kwargs):
        self.a = a
        super().__init__(**kwargs)

    def __str__(self):
        return f'A={self.a}'


class B:
    def __init__(self, b, **kwargs):
        self.b = b
        super().__init__(**kwargs)

    def __str__(self):
        return f'B={self.b}'


class C(A, B):
    def __init__(self, a, b, c, **kwargs):
        self.c = c
        super().__init__(a=a, b=b, **kwargs)

    def __str__(self):
        return f'{A.__str__(self)}, {B.__str__(self)}, C={self.c}'


print(C(1, 2, 3))
