import re
import random
from ..strategy import Strategy
from .type_mutators import IntMutator
from .type_mutators import FloatMutator
from .type_mutators import StringMutator


class PlainTextMutator:
    def __init__(self):
        self._seed = 0
        self._yields = None
        self._original = None
        self._strategy = None
        self._mutators = {str: StringMutator(), int: IntMutator(), float: FloatMutator()}
    
    def mutate(self, _input, strategy=Strategy.NO_STRATEGY):
        self._analyse_(_input)
        self._strategy = strategy
        if self._strategy == Strategy.MAX:
            self._make_big_()
        self._yields = []
        mutated_split = []
        crazy = []
        crazyy = []
        for item in range(len(self._original)):  # goes through list of the different parts of the string to mutate
            type_item = self._get_type_(self._original[item])
            mutated = self._mutators[type_item].mutate(self._original[item])
            mutatedd = self.magic_byte_mutator(self._original[item])
            crazy.append(mutated)
            crazyy.append(mutatedd)
            copy = list(self._original)
            copy[item] = mutated
            copyy = list(self._original)
            copyy[item] = mutatedd
            mutated_split.append(copy)
            mutated_split.append(copyy)
        mutated_split.append(crazy)
        mutated_split.append(crazyy)

        for item in mutated_split: # concatenating the mutated parts together
            string = ""
            for items in item:
                string += str(items)
            if string != "":
                self._yields.append(string)

        for y in self._yields:
            if y[-1] != "\n":
                y += "\n"
            yield y

    def _analyse_(self, _input):
        """
        Given plaintext input, break up the input into its respective types
        """
        nums = re.findall(r'-?\d+\.?\d*', _input)

        self._original = []
        for num in nums:
            self._original.append(_input[:_input.index(str(num))])
            self._original.append(int(num) if self._is_int_(num) else float(num))
            n_min = _input.index(str(num)) + len(str(num))
            _input = _input[n_min:]

        self._original.append(_input)
        if self._original[-1] == "":
            del self._original[-1]
        return self._original

    def _make_big_(self):
        long = 'long ' * 50000
        other_long = 'long\n' * 50000
        self._yields.extend([long, other_long])

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
            raise Exception('Can you imagine something that will fail this?')  # non-printable bytes/surrogates need not apply

    @staticmethod
    def empty():
        return '\n'

    @staticmethod
    def magic_byte_mutator(s):
        if s == '':
            return s
        if s is type(int) or type(float):
            return s
        pos = random.randint(0, len(s) - 1)
        c = s[pos]
        bit = 1 << random.randint(0, 6)
        temp = ord(c) ^ bit
        if temp in [0x0, 0xa]:
            temp = ord(c)
        new_c = chr(temp)

        return s[:pos] + new_c + s[pos + 1:]
