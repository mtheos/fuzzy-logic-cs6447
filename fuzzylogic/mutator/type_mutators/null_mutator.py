class NullMutator:
    def __init__(self):
        self.seed = 0

    @staticmethod
    def mutate(x):
        return x

    @staticmethod
    def deterministic_mutator(i, strategy):
        return [None]
        # todo: do different shit depending on the strategy
        # if strategy is "true":
        #     return [True]
        # if strategy is "false":
        #     return [False]
        # if strategy == 'make_zero':
        #     return [True, False]
        # else:
        #     return [i]
