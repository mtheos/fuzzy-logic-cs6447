class CsvMutator:
    def __init__(self):
        self.seed = 0

    # return a generator
    def mutate(self, csv_object):
        self.seed += 1
        for x in ['', '', csv_object, csv_object+ " "]: # note by andrew: that last item is temporary. pls delete when doing real code.
            yield x
        # todo call string_mutator or other stuff if you want.
        # aran and mikey
