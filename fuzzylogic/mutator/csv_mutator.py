import csv
from io import StringIO
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .csv_row_mutator import CsvRowMutator


class CsvMutator:
    def __init__(self):
        self._seed = 0
        self._mutators = {}
        self._row_mutator = CsvRowMutator()
        self._original = None  # Dictionary of json
        self._has_headers = False
        self._headers = None  # List of keys in json
        self._field_type = None  # Dictionary of key:type

    # return a generator (i.e. list)
    def mutate(self, csv_input):
        # print('\n\n**********')
        # print('Mutator called with input')
        # print(csv_input)
        # print('**********\n\n')
        self._analyse_(csv_input)
        # output = list([list(x) for x in self._original])
        # for i in range(20):
        #     self._row_mutator.mutate(output)
        #     stream = StringIO()
        #     csv.writer(stream).writerows(output)
        #     output2 = stream.getvalue()
        #     output2 = output2.replace('\r', '')
        #     yield output2
        start = 1 if self._has_headers else 0
        for idx in range(start, len(self._original)):
            for jdx in range(len(self._original[idx])):
                self._seed += 1
                output = list([list(x) for x in self._original])
                output = self._mutate_(output, idx, jdx)
                stream = StringIO()
                csv.writer(stream).writerows(output)
                output = stream.getvalue()
                output = output.replace('\r', '')
                yield output
        output = list([list(x) for x in self._original])
        self._row_mutator.mutate(output)
        stream = StringIO()
        csv.writer(stream).writerows(output)
        output = stream.getvalue()
        output = output.replace('\r', '')
        yield output

    def _mutate_(self, output, idx, jdx):
        type_mutator = self._get_mutator_((idx, jdx))
        output[idx][jdx] = type_mutator.mutate(output[idx][jdx])
        return output

    def _analyse_(self, _input):
        reader = csv.reader(_input.splitlines())
        self._original = [r for r in reader]
        try:
            self._has_headers = csv.Sniffer().has_header(_input)
        except csv.Error:
            self._has_headers = False
        self._headers = self._original[0] if self._has_headers else None
        self._build_types_()

    def _build_types_(self):
        self._field_type = {}
        for idx in range(len(self._original)):
            for jdx in range(len(self._original[idx])):
                self._field_type[(idx, jdx)] = self._get_type_(self._original[idx][jdx])
                self._original[idx][jdx] = self._field_type[(idx, jdx)](self._original[idx][jdx])
                # print(f'Key ({idx}, {jdx}) => type {self._field_type[(idx, jdx)]}')

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
