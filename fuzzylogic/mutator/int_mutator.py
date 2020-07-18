import random


class IntMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        options = [
            self.add_mutation, 
            self.minus_mutation,
            self.meme_mutation
            ]
        mutator = random.choice(options)
        return mutator(i)
    
    def meme_mutation(self,i):
        options = [0, (2**31) - 1, -(2**31), (2**32) - 1]
        return random.choice(options)

    def add_mutation(self, i):  # % by max int if max int is provided (??)
        i += random.randint(1, 1000000)
        return i 

    def minus_mutation(self, i):
        i -= random.randint(1, 1000000)
        return i
