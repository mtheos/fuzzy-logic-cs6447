import random


class IntMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        options = [
            self._add_mutation_,
            self._minus_mutation_,
            self._meme_mutation_
        ]
        mutator = random.choice(options)
        return mutator(i)

    @staticmethod
    def _meme_mutation_(_):
        options = [0, (2 ** 31) - 1, -(2 ** 31), (2 ** 32) - 1]
        return random.choice(options)

    @staticmethod
    def _add_mutation_(i):  # % by max int if max int is provided (??)
        i += random.randint(1, 1000000)
        return i

    @staticmethod
    def _minus_mutation_(i):
        i -= random.randint(1, 1000000)
        return i

    @staticmethod
    def deterministic_mutator(i, strategy):
        if strategy == "increment":
            return [i + 1]
        if strategy == "decrement":
            return [i - 1]
        if strategy == "zero":
            return 0
        if strategy == "max":
            return [2 ** 31 - 1]
        if strategy == "min":
            return [-(2 ** 31)]
        if strategy == 'make_zero':
            return [i - 1, i + 1, 0, 2 ** 31 - 1, 0 - 2 ** 31]
        else:
            return [i]
