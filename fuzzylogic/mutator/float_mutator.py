import random


class FloatMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, f):
        options = [
            self._add_mutation_, 
            self._minus_mutation_,
            self._meme_mutation_,
            ]
        mutator = random.choice(options)
        return mutator(f)

    def _meme_mutation_(self, f):
        options = [0, float('-inf'), float('inf'), float('NaN')]
        return random.choice(options)

    def _add_mutation_(self, f):  # % by max int if max int is provided (??)
        f += random.uniform(0, 1000000)
        return f 

    def _minus_mutation_(self, f):
        f -= random.uniform(1, 1000000)
        return f

    def deterministic_mutator(self, i, strategy):
        if strategy is "increment":
            return [i+1]
        if strategy is "decrement":
            return [i-1]
        if strategy is "zero":
            return [0]
        if strategy is "min":
            return [float("-inf")]
        if strategy is "max":
            return [float("inf")]
        if strategy is "na":
            return [float("NaN")]
        if strategy == 'make_zero':
            return [i-1, i+1, 0, float('-inf'), float('inf'), float('NaN')]
        else:
            return [i]
