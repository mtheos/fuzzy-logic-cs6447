import random
from ...strategy import Strategy


class StringMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, s):  # choose one mutating option
        options = [
            self._del_rand_chars_,
            self._flip_rand_chars_,
            self._insert_rand_chars_,
            self._meme_mutation_,
            self._insert_fmt_str_
        ]
        mutator = random.choices(options, weights=[1, 3, 5, 1, 3], k=1)[0]
        return mutator(s)

    def _meme_mutation_(self, s):
        options = [
            '',
            self._adamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadam_generator(),
            self._insert_rand_newline_(s)
        ]
        return random.choice(options)

    @staticmethod
    def _del_rand_chars_(s):
        if s == '':
            return s
        pos = random.randint(0, len(s) - 1)
        return s[:pos] + s[pos + 1:]

    @staticmethod
    def _insert_rand_chars_(s):
        pos = random.randint(0, len(s))
        random_character = chr(random.randrange(32, 127))
        return s[:pos] + random_character + s[pos:]

    @staticmethod
    def _flip_rand_chars_(s):
        if s == '':
            return s
        pos = random.randint(0, len(s) - 1)
        c = s[pos]
        bit = 1 << random.randint(0, 6)
        temp = ord(c) ^ bit
        if temp in [0x0, 0xa]:
            temp = ord(c)
        new_c = chr(temp)
        return s[:pos] + new_c + s[pos + 1:]

    @staticmethod
    def _insert_rand_newline_(s):
        if s == '':
            return '\n'
        pos = random.randint(0, len(s) - 1)
        return s[:pos] + '\n' + s[pos + 1:]

    @staticmethod
    def _insert_fmt_str_(s):
        if s == '':
            return '%s%n%s%n%s%n'
        pos = random.randint(0, len(s) - 1)
        return s[:pos] + '%s%n%s%n%s%n' + s[pos + 1:]

    @staticmethod
    def _adamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadam_generator():
        num = random.randint(1, 20)
        return ('adam' * 12) * num

    def deterministic_mutator(self, i, strategy):
        # todo: do different shit depending on the strategy
        mutation_list = []
        if strategy == 'append_large_string':
            return [i + self._adamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadam_generator()]

        if strategy is Strategy.ZERO:
            return [""]

        if strategy is Strategy.MAX:
            return [self._adamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadamadam_generator()]
        # byte flipping each char with the other one flipped
        if strategy is Strategy.BYTE_FLIP:
            for iterator in range(len(i)):
                temp = i
                changed_bit = ~(ord(temp[iterator]))
                flipped = temp[:iterator] + chr(changed_bit % 128) + temp[iterator + 1:]
                mutation_list.append(flipped)
            return mutation_list

        # format string 
        if strategy is Strategy.FORMAT:
            for iterator in range(len(i)):
                temp = i
                changed = temp[:iterator] + '%s%n%s%n%s%n' + temp[iterator + 1:]
                mutation_list.append(changed)
            return mutation_list

        # non ascii (unicode)
        if strategy is Strategy.NON_ASCII:
            for iterator in range(len(i)):
                temp = i
                changed = temp[:iterator] + chr(random.randint(0xA1, 0xFF00)) + temp[iterator + 1:]
                mutation_list.append(changed)
            return mutation_list

        # bitflips
        if strategy is Strategy.BIT_FLIP:
            for iterator in range(len(i)):
                temp = i
                byte = format(ord(temp[iterator]), 'b')
                for byte_it in range(len(byte)):
                    flipped_bit = self.bitflipping(int(byte[byte_it]))
                    final_byte = byte[:byte_it] + str(flipped_bit) + byte[byte_it + 1:]
                    final_byte = int(final_byte, 2)
                    final_str = temp[:iterator] + chr(final_byte) + temp[iterator + 1:]
                    mutation_list.append(final_str)

            return mutation_list

        else:
            return [i] 

    @staticmethod
    def bitflipping(i):
        # literally flips the bits because ~ doesnt work for some reason???
        return 1 if i == 0 else 0
