# these all just return literally 1 thing
# frances and aran


class IntMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        self.seed += 1
        return i


class FloatMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        self.seed += 1
        return i


class ArrayMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        self.seed += 1
        return i


class BooleanMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        self.seed += 1
        return i


class NullMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        self.seed += 1
        return i


class ObjectMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, i):
        self.seed += 1
        return i
