class Outcome:
    __slots__ = [
        'comment', 'score', 'hitScore', 'ATK', 'TER', 'DEF', 'STAT', 'END', 'INT', 'success', 'hits',
    ]

    def __init__(self, comment: str = '', score: float = 0, hitScore: float = 20, ATK: int = -1, TER: int = -1,
                 DEF: int = -1, STAT: int = -1, END: int = -1, INT: int = -1, success=False, hits: int = -1) -> None:
        super().__init__()

        self.comment: str = comment
        self.score: float = score
        self.hitScore: float = hitScore
        self.ATK: int = ATK
        self.TER: int = TER
        self.DEF: int = DEF
        self.STAT: int = STAT
        self.END: int = END
        self.INT: int = INT
        self.success = success
        self.hits: int = hits
