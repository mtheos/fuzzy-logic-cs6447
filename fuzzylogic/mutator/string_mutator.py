import random


class StringMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, s):  # choose one mutating option
        options = [
            self._del_rand_chars_, 
            self._flip_rand_chars_,
            self._insert_rand_chars_,
            self._meme_mutation_,
            self._insert_fmt_str_,
            ]
        mutator = random.choices(options, weights=[1,3,5,1,3], k=1)[0]
        return mutator(s)

    def _meme_mutation_(self, s):
        options = [
            '',
            self._adamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadam_generator(),
            self._insert_rand_newline_(s)
            ]
        return random.choice(options)

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
        temp = ord(c) ^ bit
        if temp in [0x0, 0xa]:
            temp = ord(c)
        new_c = chr(temp)
        # print("--Flipping", bit, "in", repr(c) + ", giving", repr(new_c))
        return s[:pos] + new_c + s[pos + 1:]

    def _insert_rand_newline_(self, s):
        if s == "":
            return "\n"
        pos = random.randint(0, len(s) - 1)
        return s[:pos] + '\n' + s[pos+1:]
    
    def _insert_fmt_str_(self, s):
        if s == "":
            return "%s"
        pos = random.randint(0, len(s) - 1)
        return s[:pos] + '%s' + s[pos+1:]
    
    def _adamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadam_generator(self):
        num = random.randint(1,20)
        return ("adam"*12) * num


