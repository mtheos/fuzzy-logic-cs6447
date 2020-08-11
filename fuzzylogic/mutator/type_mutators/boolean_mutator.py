from ...strategy import Strategy


class BooleanMutator:
    def __init__(self):
        self.seed = 0

    @staticmethod
    def mutate(boo):
        return not boo

    @staticmethod
    def deterministic_mutator(i, strategy):

        if strategy == "true":
            return [True, 1, '1']
        if strategy == "false":
            return [False, 0, '']

        if strategy == Strategy.MAKE_ZERO:
            return [True, False]
        else:
            return [i]
