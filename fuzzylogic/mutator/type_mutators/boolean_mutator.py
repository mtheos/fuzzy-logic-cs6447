class BooleanMutator:
    def __init__(self):
        self.seed = 0

    @staticmethod
    def mutate(boo):
        return not boo

    @staticmethod
    def deterministic_mutator(i, strategy):
        # todo: do different shit depending on the strategy
        if strategy == "true":
            return [True, 1, '1']
        if strategy == "false":
            return [False, 0, '']

        if strategy == 'make_zero':
            return [True, False]
        else:
            return [i]
