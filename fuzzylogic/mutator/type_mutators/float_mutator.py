import random


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
        if strategy == "increment":
            return [i + 1]
        if strategy == "decrement":
            return [i - 1]
        if strategy == "zero":
            return [0]
        if strategy == "min":
            return [float("-inf")]
        if strategy == "max":
            return [float("inf")]
        if strategy == "na":
            return [float("NaN")]
        if strategy == 'make_zero':
            return [i - 1, i + 1, 0, float('-inf'), float('inf'), float('NaN')]
        else:
            return [i]
