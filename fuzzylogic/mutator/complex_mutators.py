import random
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .boolean_mutator import BooleanMutator

class ObjectMutator:
    def __init__(self):
        self._mutators = {}
        self.seed = 0

    def mutate(self, obj):
        self.seed += 1
        options = [
            self.add_kv,
            self.add_kv,
            self.add_kv,
            self.add_kv,
            self.add_kv, 
            self.remove_kv, 
            self.mutate_type,
            self.mutate_type,
            self.mutate_type,
            ]
        mutator = random.choice(options)
        return mutator(obj)

    def add_kv(self, obj):
        options = [
            self.new_int,
            self.new_array,
            self.new_bool,
            self.new_none,
            self.new_obj,
            self.new_str,
            self.new_float]  # fill options with add_xyz functions
        mutator = random.choice(options)
        obj[f'new_key_{self.seed}'] = mutator()
        # print(f'-- Added: "new_key_{self.seed} {obj[f"new_key_{self.seed}"]}')
        return obj

    def remove_kv(self, obj):
        if len(list(obj.keys())) == 0:
            return obj
        rand_key = random.choice(list(obj.keys()))
        # print(f'-- Removed: {rand_key} {obj[rand_key]}')
        del obj[rand_key]
        return obj

    def mutate_type(self, obj):
        # first choose field
        if len(list(obj.keys())) == 0:
                return obj
        rand_key = random.choice(list(obj.keys()))
        # identify its type
        field_type = type(obj[rand_key])
        if field_type is int:
            obj[rand_key] = self._get_mutator_(int).mutate(obj[rand_key])
        elif field_type is str:
            obj[rand_key] = self._get_mutator_(str).mutate(obj[rand_key])
        elif field_type is float:
            obj[rand_key] = self._get_mutator_(float).mutate(obj[rand_key])
        elif field_type is list:
            obj[rand_key] = self._get_mutator_(list).mutate(obj[rand_key])  # TODO cause we haven't done yey
        elif field_type is bool:
            obj[rand_key] = self._get_mutator_(bool).mutate(obj[rand_key])
        elif field_type is dict:
            obj[rand_key] = self.mutate(obj[rand_key])
        elif field_type is None:
            print("Null mutator goes brrrrrr (doesn't exist, pls implement???)")
        # print(f'-- Mutated: {rand_key} {obj[rand_key]}')
        return obj

    def new_int(self):
        return int(random.randint(0, 10000000))

    def new_float(self):
        return float(random.uniform(0, 10000000))

    def new_str(self):
        string = 'hello'
        mut = self._get_mutator_(str)
        for i in range(0, 24):
            string = mut.mutate(string)
        return str(string)

    def new_obj(self):
        return {}

    def new_array(self):
        return []

    def new_bool(self):
        return bool(random.choice([True, False]))

    def new_none(self):
        return None
    
    def _get_mutator_(self, type_key):
        if type_key in self._mutators.keys():
            return self._mutators[type_key]

        if type_key is None:
            raise TypeError('What even is a "none" mutator?')
        elif type_key is str:
            self._mutators[str] = StringMutator()
        elif type_key is int:
            self._mutators[int] = IntMutator()
        elif type_key is float:
            self._mutators[float] = FloatMutator()
        elif type_key is bool:
            self._mutators[bool] = BooleanMutator()
        elif type_key is list:
            self._mutators[list] = ListMutator()
        elif type_key is dict:
            self._mutators[dict] = ObjectMutator()
        else:
            raise TypeError(f'*** {type_key} has an unknown type ***')
        return self._mutators[type_key]


class ListMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, lis):
        self.seed += 1
        options = [self.add_elem, self.remove_elem, self.mutate_type]
        mutator = random.choice(options)
        return mutator(lis)

    def swap_elements(self, lis):
        if len(lis) < 2:
            return lis

        pos1 = random.randint(0, len(lis) - 1)
        pos2 = random.randint(0, len(lis) - 1)
        while pos2 == pos1:
            pos2 = random.randint(0, len(lis) - 1)
        lis[pos1], lis[pos2] = lis[pos2], lis[pos1]
        return lis

    def add_elem(self, lis):
        options = [
            self.new_int,
            self.new_array,
            self.new_bool,
            self.new_none,
            self.new_obj,
            self.new_str,
            self.new_float]  # fill options with add_xyz functions
        mutator = random.choice(options)
        lis.append(mutator())
        # print(f'-- Added: {lis[::-1]}')
        return lis

    def remove_elem(self, lis):
        if len(lis) < 1:
            return lis
        rand_pos = random.randint(0, len(lis) - 1)
        # print(f'-- Removed: {lis[rand_pos]}')
        del lis[rand_pos]
        return lis

    def mutate_type(self, lis):
        # first choose field
        # TODO: If list is [] this will error
        if len(lis) == 0:
                return lis
        rand_pos = random.randint(0, len(lis) - 1)
        # identify its type
        field_type = type(lis[rand_pos])
        if field_type is int:
            lis[rand_pos] = IntMutator().mutate(lis[rand_pos])
        elif field_type is str:
            lis[rand_pos] = StringMutator().mutate(lis[rand_pos])
        elif field_type is float:
            lis[rand_pos] = FloatMutator().mutate(lis[rand_pos])
        elif field_type is list:
            lis[rand_pos] = self.mutate(lis[rand_pos])  # TODO cause we haven;t done yey
        elif field_type is bool:
            lis[rand_pos] = BooleanMutator().mutate(lis[rand_pos])
        elif field_type is dict:
            lis[rand_pos] = ObjectMutator().mutate(lis[rand_pos])
        elif field_type is None:
            print("Null mutator goes brrrrrr (doesn't exist, pls implement???)")

        # print(f'-- Mutated: {rand_pos} {lis[rand_pos]}')

        return lis

    def new_int(self):
        return int(random.randint(0, 10000000))

    def new_float(self):
        return float(random.uniform(0, 10000000))

    def new_str(self):
        string = 'hello'
        mut = StringMutator()
        for i in range(0, 24):
            string = mut.mutate(string)
        return str(string)

    def new_obj(self):
        return {}

    def new_array(self):
        return []

    def new_bool(self):
        return bool(random.choice([True, False]))

    def new_none(self):
        return None
