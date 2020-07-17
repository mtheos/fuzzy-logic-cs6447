import random
from string_mutator import StringMutator
from int_mutator import IntMutator
from float_mutator import FloatMutator
from boolean_mutator import BooleanMutator
from object_mutator import ObjectMutator

class ListMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, l):
        self.seed += 1
        options = [self.add_elem, self.remove_elem, self.mutate_type]
        mutator = random.choice(options)

        return mutator(l)

    def swap_elements(self, l):
        if len(l) < 2:
            return l
        
        pos1 = random.randint(0, len(l) - 1)
        pos2 = random.randint(0, len(l) - 1)
        while pos2 == pos1:
            pos2 = random.randint(0, len(l) - 1)
        l[pos1], l[pos2] = l[pos2], l[pos1]
        return l
    
    def add_elem(self, l):
        options = [
                self.new_int, 
                self.new_array, 
                self.new_bool, 
                self.new_none, 
                self.new_obj, 
                self.new_str, 
                self.new_float
            ] # fill options with add_xyz functions
        mutator = random.choice(options)
        l.append(mutator())
        print(f'-- Added: {l[::-1]}')
        return l

    def remove_elem(self,l):
        if len(l) < 1:
            return l
        rand_pos = random.randint(0, len(l) - 1)
        print(f'-- Removed: {l[rand_pos]}')
        del l[rand_pos]
        return l
    
    def mutate_type(self, l):
        # first choose field
        rand_pos = random.randint(0, len(l) - 1)
        # identify its type
        field_type = type(l[rand_pos])
        if field_type is int:
            l[rand_pos] = IntMutator().mutate(l[rand_pos])
        elif field_type is str:
            l[rand_pos] = StringMutator().mutate(l[rand_pos])
        elif field_type is float:
            l[rand_pos] = FloatMutator().mutate(l[rand_pos])
        elif field_type is list:
            l[rand_pos] = self.mutate(l[rand_pos]) # TODO cause we haven;t done yey
        elif field_type is bool:
            l[rand_pos] = BooleanMutator().mutate(l[rand_pos])
        elif field_type is dict:
            l[rand_pos] = ObjectMutator().mutate(l[rand_pos])
        elif field_type is None:
            print("Null mutator goes brrrrrr (doesn't exist, pls implement???)")
        
        print(f'-- Mutated: {rand_pos} {l[rand_pos]}')

        return l

    def new_int(self):
        return int(random.randint(0,10000000))
    
    def new_float(self):
        return float(random.uniform(0,10000000))

    def new_str(self):
        string = "hello"
        mut = StringMutator()
        for i in range(0,24):
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