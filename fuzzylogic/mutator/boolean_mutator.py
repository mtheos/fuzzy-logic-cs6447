class BooleanMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, boo):
        return not boo

    def deterministic_mutator(self, i, strategy):
        #todo: do different shit depending on the strategy
        if strategy is "true":
            return [True]
        if strategy is "false":
            return [False]

        if strategy == 'make_zero':
            return [True, False]
        else:
            return [i]