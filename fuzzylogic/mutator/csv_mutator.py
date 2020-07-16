class CsvMutator :
    def __init__(self):
        self.seed = 0

    # return a generator
    def mutate(self, csv_object):
        self.seed += 1
        for x in ['', '', csv_object]:
            yield x

        #todo call string_mutator or other stuff if you want. 
        #aran and mikey