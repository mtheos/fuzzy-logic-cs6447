import random


class FloatMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, f):
        options = [self._add_mutation_, self._minus_mutation_]
        mutator = random.choice(options)
        return mutator(f)

    def _add_mutation_(self, f):  # % by max int if max int is provided (??)
        f += random.uniform(0, 1000000)
        return f 

    def _minus_mutation_(self, f):
        f -= random.uniform(1, 1000000)
        return f
