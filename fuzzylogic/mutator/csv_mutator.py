import csv
from itertools import combinations
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator


class CsvMutator:
    def __init__(self):
        self._seed = 0
        self._mutators = {}
        self._original = None  # Dictionary of json
        self._header = None  # List of keys in json
        self._field_type = None  # Dictionary of key:type
        self._all = set()

    # return a generator (i.e. list)
    def mutate(self, csv_input):
        print('\n\n**********')
        print('Mutator called with input')
        print(csv_input)
        print('**********\n\n')
        self._analyse_(csv_input)
        for i in range(1, len(self._original) + 1):
            for rows_to_mutate in combinations(self._original, i):
                output = list([list(x) for x in self._original])
                for row in rows_to_mutate:
                    output = self._mutate_(output, row)
                self._seed += 1
                if output in self._all:
                    print('*****\nOutput already seen\n', output)
                    continue
                print('New mutation =>', output)
                yield output

    def _mutate_(self, output, row):
        for i in range(1, len(row) + 1):
            for rows_to_mutate in combinations(self._original, i):
                output = list([list(x) for x in self._original])
                for row in rows_to_mutate:
                    output = self._mutate_(output, row)
                self._seed += 1
                if output in self._all:
                    print('*****\nOutput already seen\n', output)
                    continue
                print('New mutation =>', output)
                yield output

        type_mutator = self._get_mutator_(row)
        output[row] = type_mutator.mutate(output[row])
        return output

    def _analyse_(self, _input):
        reader = csv.reader(_input.splitlines())
        self._original = [r for r in reader]
        self._header = None  # do this later (probably)
        self._build_types_()

    def _build_types_(self):
        self._field_type = []
        for idx, row in enumerate(self._original):
            self._field_type.append([])
            for jdx, cell in enumerate(row):
                self._field_type[idx].append(self._get_type_(cell))
                print(f'Key ({idx}, {jdx}) => type {self._field_type[idx][jdx]}')

    def _get_type_(self, v):
        if self._is_float_(v):
            return float
        elif self._is_int_(v):
            return int
        elif self._is_str_(v):
            return str
        raise TypeError(f'*** {v} is an unhandled type ***')

    @staticmethod
    def _is_float_(v):
        try:
            float(v)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_int_(v):
        try:
            int(v)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_str_(v):
        try:
            str(v)
            return True
        except ValueError:
            raise Exception('Can you imagine something that will fail this?')

    def _get_mutator_(self, key):
        if self._field_type[key] not in self._mutators:
            if self._field_type[key] is None:
                raise TypeError('What even is a "none" mutator?')
            elif self._field_type[key] is str:
                self._mutators[str] = StringMutator()
            elif self._field_type[key] is int:
                self._mutators[int] = IntMutator()
            elif self._field_type[key] is float:
                self._mutators[float] = FloatMutator()
            # elif self._field_type[key] is bool:
                # self._mutators[bool] = BooleanMutator()
            # elif self._field_type[key] is list:
            #     self._mutators[list] = ListMutator()
            # elif self._field_type[key] is dict:
            #     self._mutators[dict] = ObjectMutator()
            else:
                raise TypeError(f'*** {key} has an unknown type ***')
        return self._mutators[self._field_type[key]]

    def empty(self):
        return ""
