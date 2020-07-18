import json
from itertools import combinations
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .boolean_mutator import BooleanMutator
from .complex_mutators import ListMutator, ObjectMutator


class JsonMutator:
    def __init__(self):
        self._seed = 0
        self._mutators = {}
        self._original = None    # Dictionary of json
        self._keys = None        # List of keys in json
        self._field_type = None  # Dictionary of key:type
        self._all = set()

    # return a generator (i.e. list)
    def mutate(self, json_input):
        print('\n\n**********')
        print('Mutator called with input')
        print(json_input)
        print('**********\n\n')
        self._analyse_(json_input)
        # combinations will return objects like this for i = 1 to n
        # [(key1,), (key2,), (key3,)]
        # [(key1, key2), (key1, key3), (key2, key3)]
        # [(key1, key2, key3)]
        for i in range(1, len(self._keys) + 1):
            for keys_to_mutate in combinations(self._keys, i):
                output = dict(self._original)
                # print('mutating:', ', '.join(keys_to_mutate))
                for key in keys_to_mutate:
                    self._mutate_(output, key)
                self._seed += 1
                output = json.dumps(output)
                if output in self._all:
                    print('*****\nOutput already seen\n', output)
                    continue
                print('New mutation =>', output)
                yield output

    def _mutate_(self, output, key):
        type_mutator = self._get_mutator_(key)
        output[key] = type_mutator.mutate(output[key])

    def _analyse_(self, _input):
        self._original = json.loads(_input)
        self._keys = [x for x in self._original.keys()]
        self._build_types_()

    def _build_types_(self):
        self._field_type = {}
        for k, v in self._original.items():
            self._field_type[k] = self._get_type_(v)
            # print(f'Key {k} => type {self._field_type[k]}')

    @staticmethod
    def _get_type_(v):
        field_type = type(v)
        if field_type not in [None, str, int, float, bool, list, dict]:
            raise TypeError(f'*** {v} is an unknown type ***')
        return field_type

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
            elif self._field_type[key] is bool:
                self._mutators[bool] = BooleanMutator()
            elif self._field_type[key] is list:
                self._mutators[list] = ListMutator()
            elif self._field_type[key] is dict:
                self._mutators[dict] = ObjectMutator()
            else:
                raise TypeError(f'*** {key} has an unknown type ***')
        return self._mutators[self._field_type[key]]

    def empty(self):
        return json.dumps(json.loads("{}"))  # i think this is right? this gets plugged into a mutator
