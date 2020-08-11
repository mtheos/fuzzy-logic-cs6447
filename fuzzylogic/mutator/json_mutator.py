import json
from ..strategy import Strategy
from .type_mutators import IntMutator
from .type_mutators import NullMutator
from .type_mutators import FloatMutator
from .type_mutators import StringMutator
from .type_mutators import BooleanMutator
from .type_mutators import ListMutator, ObjectMutator


class JsonMutator:
    def __init__(self):
        self._seed = 0
        self._mutators = {}
        self._yields = None
        self._strategy = None
        self._keys = None        # List of keys in json
        self._original = None    # Dictionary of json
        self._field_type = None  # Dictionary of key:type
        self._static_mutators = {type(None): NullMutator, str: StringMutator(), int: IntMutator(), float: FloatMutator(), bool: BooleanMutator()}

    def mutate(self, json_input, strategy=Strategy.NO_STRATEGY):
        self._strategy = strategy
        try:
            self._analyse_(json_input)
        except RecursionError:
            return  # probably a meme
        if self._strategy == Strategy.NO_STRATEGY:
            for key in self._keys:
                self._seed += 1
                output = dict(self._original)
                output = json.dumps(self._mutate_(output, key))
                if output[-1] != '\n':
                    output += '\n'
                yield output
        else:
            self._yields = []
            self.recurse(self._original)
            if self._strategy == Strategy.MAX:
                self._make_big_()
            for y in self._yields:
                if y[-1] != '\n':
                    y += '\n'
                yield y

    def recurse(self, original):
        # big TODO for andrew: make this also insert shit into dicts and lists
        if type(original) is dict:
            if self._strategy == Strategy.ADD_DICTS:
                for i in range(Strategy.members_to_add_to_dict): # who cares if we overwrite existing shit
                    original["additional_meme"+str(i)] = "some nice cool sample meme"
                self._yields.append(json.dumps(self._original))
                for i in range(Strategy.members_to_add_to_dict):
                    del original["additional_meme"+str(i)]
            for k, v in original.items():
                if type(v) is dict:
                    self.recurse(v)
                elif type(v) is list:
                    self.recurse(v)
                else:
                    # get the static mutator for whatever type it is
                    for mutation in self._static_mutators[type(v)].deterministic_mutator(v, self._strategy):
                        tmp = v
                        original[k] = mutation
                        self._yields.append(json.dumps(self._original))
                        original[k] = tmp
        elif type(original) is list:
            for k in range(len(original)):
                v = original[k]
                if type(v) is dict:
                    self.recurse(v)
                elif type(v) is list:
                    self.recurse(v)
                else:
                    for mutation in self._static_mutators[type(v)].deterministic_mutator(v, self._strategy):
                        tmp = v
                        original[k] = mutation
                        self._yields.append(json.dumps(self._original))
                        original[k] = tmp

    def _make_big_(self):
        flat = '{'
        flat += '"flat": "hi",' * (50000 - 1)
        flat += '"flat": "hi"'
        flat += '}'

        nested = '{'
        nested += '"nested": {' * 50000
        nested += '"nested": "hi"'
        nested += '}' * 50000
        nested += '}'
        self._yields.extend([flat, nested])

    def _mutate_(self, output, key):
        type_mutator = self._get_mutator_(key)
        output[key] = type_mutator.mutate(output[key])
        return output

    def _analyse_(self, _input):
        self._original = json.loads(_input)
        self._keys = [x for x in self._original.keys()]
        self._build_types_()

    def _build_types_(self):
        self._field_type = {}
        for k, v in self._original.items():
            self._field_type[k] = self._get_type_(v)

    @staticmethod
    def _get_type_(v):
        field_type = type(v)
        if field_type not in [type(None), str, int, float, bool, list, dict]:
            raise TypeError(f'*** {v} is an unknown type ***')
        return field_type

    def _get_mutator_(self, key):
        if self._field_type[key] not in self._mutators:
            if self._field_type[key] is type(None):
                self._mutators[type(None)] = NullMutator()
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
        return self._mutators[self._field_type[key]]

    @staticmethod
    def empty():
        return '{}\n'
