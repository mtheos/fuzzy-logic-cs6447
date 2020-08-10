import re
from .type_mutators import IntMutator
from .type_mutators import FloatMutator
from .type_mutators import StringMutator


class PlainTextMutator:
    def __init__(self):
        self._seed = 0
        self.yields = None
        self._original = None
        self._mutators = {str: StringMutator(), int: IntMutator(), float: FloatMutator()}
    
    def mutate(self, _input, strategy='none'):
        self._analyse_(_input)
        self.yields = []
        mutated_split = []
        crazy = []
        for item in range(len(self._original)):
            # print("we are mutating", self._original[item])
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

        for y in self.yields:
            if y[-1] != "\n":
                y += "\n"
                yield y

        return self.yields

    def _analyse_(self, _input):
        """
        Given plaintext input, break up the input into its respective types
        """
        nums = re.findall(r'-?\d+\.?\d*', _input)
        # nums = [self._get_type_(x)(x) for x in nums]
        # nums = [x for x in nums]
        print(nums)

        self._original = []
        for num in nums:
            self._original.append(_input[:_input.index(str(num))])
            self._original.append(int(num))
            n_min = _input.index(str(num)) + len(str(num))
            _input = _input[n_min:]
        # print("nums is", nums)
        self._original.append(_input)
        # print("before", self._original)
        # self._original = list(filter(None, self._original))
        if self._original[-1] is "":
            del self._original[-1]
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
            # raise ValueError('This error is in _is_str_ in csv mutator')
            # OK, now that I have your attention. This function won't work
            # Almost anything can be represented as a string, the str function
            # will only fail if your input has non printable bytes \x00 \x01 etc
            # You need to assume str if your other checks all fail
            str(v)
            return True
        except ValueError:
            return False

    @staticmethod
    def empty():
        return '\n'
