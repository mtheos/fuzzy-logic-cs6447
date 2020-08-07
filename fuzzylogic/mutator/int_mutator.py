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
    
    def _meme_mutation_(self, i):
        options = [0, (2**31) - 1, -(2**31), (2**32) - 1]
        return random.choice(options)

    def _add_mutation_(self, i):  # % by max int if max int is provided (??)
        i += random.randint(1, 1000000)
        return i 

    def _minus_mutation_(self, i):
        i -= random.randint(1, 1000000)
        return i

    def deterministic_mutator(self, i, strategy):
        if strategy is "increment":
            return [i+1]

        if strategy is "decrement":
            return [i-1]
        
        if strategy is "zero":
            return 0

        if strategy is "max":
            return [2**31-1]
        
        if strategy is "min":
            return [-(2**31)]

        if strategy == 'make_zero':
            return [i-1, i+1, 0, 2**31-1, 0-2**31]
        else:
            return [i]
