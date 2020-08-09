import re

from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .boolean_mutator import BooleanMutator
from .complex_mutators import ListMutator, ObjectMutator

class PlainTextMutator:
    def __init__(self):
        self._seed = 0
        self._original = None
        self._mutators = {str:StringMutator(), int:IntMutator(), float:FloatMutator()}
        self.yields = None
    
    def mutate(self, _input, strategy='none'):
        self._analyse_(_input)

        self.yields = []
        mutated_split = []
        crazy = []
        for item in range(len(self._original)):
            type_item = self._get_type_(self._original[item])
            # print("original",self._original[item])
            if strategy is "none":
                mutated = self._mutators[type_item].mutate(self._original[item])
            else:
                mutated = self._mutators[type_item].deterministic_mutator(self._original[item], strategy)
            crazy.append(mutated)
            copy = list(self._original)
            copy[item] = mutated
            # print("copy is", copy)
            mutated_split.append(copy)
            # print("yield is currently", self.yields)
        mutated_split.append(crazy)
        for item in mutated_split:
            # print(item)
            string = ""
            for items in item:
                string += str(items)
            self.yields.append(string)

        return self.yields


    def _analyse_(self, _input):
        """
        Given plaintext input, break up the input into its respective types
        """
        nums = re.findall(r'-?\d+\.?\d*',_input)
        nums = [self._get_type_(x)(x) for x in nums]

        self._original = []
        for num in nums:
            self._original.append(_input[:_input.index(str(num))])
            self._original.append(num)
            min = _input.index(str(num)) + len(str(num))
            _input = _input[min:]
        self._original.append(_input)
        self._original = list(filter(None, self._original))
        return self._original

    def _get_type_(self, v):
        if self._is_int_(v):
            return int
        elif self._is_float_(v):
            return float
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
            return False