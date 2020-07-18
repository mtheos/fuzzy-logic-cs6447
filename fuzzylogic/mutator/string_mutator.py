import random


class StringMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, s):  # choose one mutating option
        options = [
            self._del_rand_chars_, 
            self._flip_rand_chars_,
            self._flip_rand_chars_,
            self._flip_rand_chars_,
            self._insert_rand_chars_,
            self._insert_rand_chars_,
            self._insert_rand_chars_,
            self._insert_rand_chars_,
            self._insert_rand_chars_
            ]
        mutator = random.choice(options)
        return mutator(s)

    def _del_rand_chars_(self, s):
        if s == "":
            return s
        pos = random.randint(0, len(s) - 1)
        # print("--Deleting", repr(s[pos]), "at", pos)
        return s[:pos] + s[pos + 1:]

    def _insert_rand_chars_(self, s):
        pos = random.randint(0, len(s))
        random_character = chr(random.randrange(32, 127))
        # print("--Inserting", repr(random_character), "at", pos)
        return s[:pos] + random_character + s[pos:]

    def _flip_rand_chars_(self, s):
        if s == "":
            return s
        pos = random.randint(0, len(s) - 1)
        c = s[pos]
        bit = 1 << random.randint(0, 6)
        new_c = chr(ord(c) ^ bit)
        # print("--Flipping", bit, "in", repr(c) + ", giving", repr(new_c))
        return s[:pos] + new_c + s[pos + 1:]
