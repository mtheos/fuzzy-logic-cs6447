class NullMutator:
    def __init__(self):
        self.seed = 0

    @staticmethod
    def mutate(x):
        return x

    @staticmethod
    def deterministic_mutator(i, strategy):
        return [None]
