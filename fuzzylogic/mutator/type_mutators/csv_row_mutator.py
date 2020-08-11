import random
from .string_mutator import StringMutator


class CsvRowMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, csv, num=0):  # choose one mutating option
        if num == 0:
            num = random.randint(1, 10)
        for i in range(num):
            self._add_row_(csv)
        return csv

    def _add_row_(self, csv):
        if len(csv) == 0:
            return csv

        options = [
            self._new_int_,
            self._new_float_,
            self._new_string_,
            self._empty_string_
        ]

        row_len = len(csv[0])
        new_row = []

        for i in range(row_len):
            mut = random.choice(options)
            new_row.append(mut())

        csv.append(new_row)
        return csv

    @staticmethod
    def _empty_string_():
        return ''

    @staticmethod
    def _new_string_():
        string = "hello"
        mut = StringMutator()
        for i in range(0, 24):
            string = mut.mutate(string)
        return str(string)

    @staticmethod
    def _new_int_():
        return int(random.randint(0, 10000000))

    @staticmethod
    def _new_float_():
        return float(random.uniform(0, 10000000))
