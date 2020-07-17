import json
from itertools import combinations
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .int_mutator import ArrayMutator
from .boolean_mutator import BooleanMutator
# from .int_mutator import ObjectMutator


class JsonMutator:
    def __init__(self):
        self._seed = 0
        self._original = None  # Dictionary of json
        self._keys = None  # List of keys in json
        self._field_type = None  # Dictionary of key:type

    # return a generator (i.e. list)
    def mutate(self, json_input):
        self._analyse_(json_input)
        # combinations will return objects like this for i = 1 to n
        # [(key1,), (key2,), (key3,)]
        # [(key1, key2), (key1, key3), (key2, key3)]
        # [(key1, key2, key3)]
        for i in range(1, len(self._keys) + 1):
            for keys_to_mutate in combinations(self._keys, i):
                output = dict(self._original)
                print('mutating:', ', '.join(keys_to_mutate))
                for key in keys_to_mutate:
                    self._mutate_(output, key)
                self._seed += 1
                yield output

    def _mutate_(self, output, key):
        type_mutator = self._get_mutator_(key)
        if self._field_type[key] == 'int':
            output[key] = type_mutator().mutate(output[key])

    def _analyse_(self, _input):
        self._original = json.loads(_input)
        self._keys = [x for x in self._original.keys()]
        self._build_types_()

    def _build_types_(self):
        self._field_type = {}
        for k, v in self._original.items():
            self._field_type[k] = self._get_type_(v)
            print(f'{k} => {self._field_type[k]}')

    @staticmethod
    def _get_type_(v):
        if v is None:
            return 'none'
        elif isinstance(v, str):
            return 'str'
        elif isinstance(v, int):
            return 'int'
        elif isinstance(v, float):
            return 'float'
        elif isinstance(v, list):
            return 'list'
        elif isinstance(v, dict):
            return 'dict'
        elif isinstance(v, bool):
            return 'bool'
        else:
            return 'unknown'
            # raise TypeError(f'*** {v} is an unknown type ***')

    def _get_mutator_(self, key):
        if self._field_type[key] == 'none':
            raise TypeError('What even is a "none" mutator?')
        elif self._field_type[key] == 'str':
            raise TypeError('String mutator not found')
        elif self._field_type[key] == 'int':
            return IntMutator
        elif self._field_type[key] == 'float':
            return FloatMutator
        elif self._field_type[key] == 'list':
            return ArrayMutator
        elif self._field_type[key] == 'dict':
            raise TypeError('Dict/Object mutator not found')
            # return ObjectMutator
        elif self._field_type[key] == 'bool':
            return BooleanMutator
        elif self._field_type[key] == 'unknown':
            raise TypeError(f'*** {key} has an unknown type ***')