import random
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator

class CsvRowMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, csv, num = 1):  # choose one mutating option
        for i in range(num):
            self._add_row_(csv)
        return csv
    
    def _add_row_(self, csv):
        if len(csv) == 0:
            raise ValueError("why is a CSV empty???") # empty csv case??

        options = [
            self._new_int_,
            self._new_float_,
            self._new_string_,
            self._empty_string_,
        ]

        row_len = len(csv[0])
        new_row = []
        
        for i in range(row_len):
            mut = random.choice(options)
            new_row.append(mut())
        
        csv.append(new_row)
        return csv
    
    def _empty_string_(self):
        return ''
    
    def _new_string_(self):
        string = "hello"
        mut = StringMutator()
        for i in range(0, 24):
            string = mut.mutate(string)
        return str(string)

    def _new_int_(self):
        return int(random.randint(0, 10000000))

    def _new_float_(self):
        return float(random.uniform(0, 10000000))

