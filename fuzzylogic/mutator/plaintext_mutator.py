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
        raise TypeError(f'*** {v} is an unhandled type ***')

    def _is_float_(self, v):
        try:
            float(v)
            return True
        except ValueError:
            return False

    def _is_int_(self, v):
        try:
            int(v)
            return True
        except ValueError:
            return False