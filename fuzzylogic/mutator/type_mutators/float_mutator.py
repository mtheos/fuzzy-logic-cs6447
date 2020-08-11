import random
from ...strategy import Strategy


class FloatMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, f):
        options = [
            self._add_mutation_,
            self._minus_mutation_,
            self._meme_mutation_
        ]
        mutator = random.choice(options)
        return mutator(f)

    @staticmethod
    def _meme_mutation_(_):
        options = [0, float('-inf'), float('inf'), float('NaN')]
        return random.choices(options, weights=[3, 4, 4, 4], k=1)

    @staticmethod
    def _add_mutation_(f):  # % by max int if max int is provided (??)
        f += random.uniform(0, 1000000)
        return f

    @staticmethod
    def _minus_mutation_(f):
        f -= random.uniform(1, 1000000)
        return f

    @staticmethod
    def deterministic_mutator(i, strategy):
        if strategy is Strategy.INCREMENT:
            return [i+1]
        if strategy is Strategy.DECREMENT:
            return [i-1]
        if strategy is Strategy.ZERO:
            return [0]
        if strategy is Strategy.MIN:
            return [float("-inf")]
        if strategy is Strategy.MAX:
            return [float("inf")]
        if strategy is Strategy.NAN:
            return [float("NaN")]
        if strategy == Strategy.MAKE_ZERO:
            return [i-1, i+1, 0, float('-inf'), float('inf'), float('NaN')]
        else:
            return [i]
