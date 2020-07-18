import random


class FloatMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, f):
        options = [
            self.add_mutation, 
            self.minus_mutation,
            self.meme_mutation,
            ]
        mutator = random.choice(options)
        return mutator(f)

    def meme_mutation(self, f):
        options = [0, float('-inf'), float('inf'), float('NaN')]
        return random.choice(options)

    def add_mutation(self, f):  # % by max int if max int is provided (??)
        f += random.uniform(0, 1000000)
        return f 

    def minus_mutation(self, f):
        f -= random.uniform(1, 1000000)
        return f
