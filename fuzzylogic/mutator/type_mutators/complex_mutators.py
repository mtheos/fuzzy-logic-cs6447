import random
from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .boolean_mutator import BooleanMutator


class ObjectMutator:
    def __init__(self):
        self._mutators = {}
        self.seed = 0
        self.depth = 0

    def mutate(self, obj):
        self.seed += 1
        self.depth += 1
        if self.depth >= 1000:
            self.depth -= 1
            return obj
        options = [
            self._add_kv_,
            self._remove_kv_,
            self._mutate_type_,
        ]
        mutator = random.choices(options, weights=[5, 1, 3], k=1)[0]
        self.depth -= 1
        return mutator(obj)

    def _add_kv_(self, obj):
        options = [
            self._new_int_,
            self._new_array_,
            self._new_bool_,
            self._new_none_,
            self._new_obj_,
            self._new_str_,
            self._new_float_
        ]  # fill options with add_xyz functions
        mutator = random.choice(options)
        obj[f'new_key_{self.seed}'] = mutator()
        return obj

    @staticmethod
    def _remove_kv_(obj):
        if len(list(obj.keys())) == 0:
            return obj
        rand_key = random.choice(list(obj.keys()))
        del obj[rand_key]
        return obj

    def _mutate_type_(self, obj):
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

    @staticmethod
    def _new_int_():
        return int(random.randint(0, 10000000))

    @staticmethod
    def _new_float_():
        return float(random.uniform(0, 10000000))

    def _new_str_(self):
        string = "hello"
        mut = self._get_mutator_(str)
        for i in range(0, 24):
            string = mut.mutate(string)
        return str(string)

    def _new_obj_(self):
        num = random.randint(5, 25)
        new = {}
        for i in range(num):
            self.depth += 1
            if self.depth < 20:
                new = self.mutate(new)
            self.depth -= 1
        return new

    @staticmethod
    def _new_array_():
        return []

    @staticmethod
    def _new_bool_():
        return bool(random.choice([True, False]))

    @staticmethod
    def _new_none_():
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
        self._mutators = {}
        self.seed = 0

    def mutate(self, lis):
        self.seed += 1
        options = [
            self._add_elem_,
            self._remove_elem_,
            self._mutate_type_,
            self._swap_elements_,
        ]
        mutator = random.choices(options, weights=[5, 1, 3, 1], k=1)[0]
        return mutator(lis)

    @staticmethod
    def _swap_elements_(lis):
        if len(lis) < 2:
            return lis
        pos1 = random.randint(0, len(lis) - 1)
        pos2 = random.randint(0, len(lis) - 1)
        while pos2 == pos1:
            pos2 = random.randint(0, len(lis) - 1)
        lis[pos1], lis[pos2] = lis[pos2], lis[pos1]
        return lis

    def _add_elem_(self, lis):
        options = [
            self._new_int_,
            self._new_array_,
            self._new_bool_,
            self._new_none_,
            self._new_obj_,
            self._new_str_,
            self._new_float_]  # fill options with add_xyz functions
        mutator = random.choice(options)
        lis.append(mutator())
        return lis

    @staticmethod
    def _remove_elem_(lis):
        if len(lis) < 1:
            return lis
        rand_pos = random.randint(0, len(lis) - 1)
        del lis[rand_pos]
        return lis

    def _mutate_type_(self, lis):
        # first choose field
        if len(lis) == 0:
            return lis
        rand_pos = random.randint(0, len(lis) - 1)
        # identify its type
        field_type = type(lis[rand_pos])
        if field_type is int:
            lis[rand_pos] = self._get_mutator_(int).mutate(lis[rand_pos])
        elif field_type is str:
            lis[rand_pos] = self._get_mutator_(str).mutate(lis[rand_pos])
        elif field_type is float:
            lis[rand_pos] = self._get_mutator_(float).mutate(lis[rand_pos])
        elif field_type is list:
            lis[rand_pos] = self.mutate(lis[rand_pos])  # TODO cause we haven't done yey
        elif field_type is bool:
            lis[rand_pos] = self._get_mutator_(bool).mutate(lis[rand_pos])
        elif field_type is dict:
            lis[rand_pos] = self._get_mutator_(dict).mutate(lis[rand_pos])
        elif field_type is None:
            print("Null mutator goes brrrrrr (doesn't exist, pls implement???)")

        return lis

    @staticmethod
    def _new_int_():
        return int(random.randint(0, 10000000))

    @staticmethod
    def _new_float_():
        return float(random.uniform(0, 10000000))

    def _new_str_(self):
        string = 'hello'
        mut = self._get_mutator_(str)
        for i in range(0, 24):
            string = mut.mutate(string)
        return str(string)

    @staticmethod
    def _new_obj_():
        return {}

    @staticmethod
    def _new_array_():
        return []

    @staticmethod
    def _new_bool_():
        return bool(random.choice([True, False]))

    @staticmethod
    def _new_none_():
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
