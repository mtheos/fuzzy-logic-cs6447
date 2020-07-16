class CsvMutator :
    def __init__(self):
        self.seed = 0
    def mutate(self, csv_object):
        self.seed += 1
        return csv_object