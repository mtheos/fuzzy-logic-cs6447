import random
#these all just return literally 1 thing
#frances and aran
class IntMutator : 
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        options = [self.add_mutation, self.minus_mutation]
        mutator = random.choice(options)
        return mutator(i)

    def add_mutation(self,i): # % by max int if max int is provided (??)
        i = i + random.randint(1,1000000)
        return i 

    def minus_mutation(self,i):
        i = i - random.randint(1,1000000)
        return i

# class NullMutator:
#     def __init__(self):
#         self.seed = 0

#     def mutate(self, i):
#         self.seed += 1
#         return i
