class BooleanMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, boo):
        return not boo
