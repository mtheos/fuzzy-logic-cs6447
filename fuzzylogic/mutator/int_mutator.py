import random


class IntMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        options = [self.add_mutation, self.minus_mutation]
        mutator = random.choice(options)
        return mutator(i)

    def add_mutation(self, i):  # % by max int if max int is provided (??)
        i += random.randint(1, 1000000)
        return i 

    def minus_mutation(self, i):
        i -= random.randint(1, 1000000)
        return i
