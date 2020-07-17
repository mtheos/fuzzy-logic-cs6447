import random


class StringMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, s):  # choose one mutating option
        options = [self.del_rand_chars, self.insert_rand_chars, self.flip_rand_chars]
        mutator = random.choice(options)
        return mutator(s)

    def del_rand_chars(self, s):
        if s == "":
            return s
        pos = random.randint(0, len(s) - 1)
        # print("--Deleting", repr(s[pos]), "at", pos)
        return s[:pos] + s[pos + 1:]

    def insert_rand_chars(self,s):
        pos = random.randint(0, len(s))
        random_character = chr(random.randrange(32, 127))
        # print("--Inserting", repr(random_character), "at", pos)
        return s[:pos] + random_character + s[pos:]

    def flip_rand_chars(self,s):
        if s == "":
            return s
        pos = random.randint(0, len(s) - 1)
        c = s[pos]
        bit = 1 << random.randint(0, 6)
        new_c = chr(ord(c) ^ bit)
        # print("--Flipping", bit, "in", repr(c) + ", giving", repr(new_c))
        return s[:pos] + new_c + s[pos + 1:]