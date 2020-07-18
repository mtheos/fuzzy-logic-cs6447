import random


class IntMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        options = [self._add_mutation_, self._minus_mutation_]
        mutator = random.choice(options)
        return mutator(i)

    def _add_mutation_(self, i):  # % by max int if max int is provided (??)
        i += random.randint(1, 1000000)
        return i 

    def _minus_mutation_(self, i):
        i -= random.randint(1, 1000000)
        return i
