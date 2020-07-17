import random
from string_mutator import StringMutator
from int_mutator import IntMutator
from float_mutator import FloatMutator
from boolean_mutator import BooleanMutator

class ObjectMutator:
    def __init__(self):
        self.seed = 0

    def mutate(self, o):
        self.seed += 1
        options = [self.add_kv, self.remove_kv, self.mutate_type]
        mutator = random.choice(options)

        return mutator(o)

    def add_kv(self, o):
        
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
        o[f"new_key_{self.seed}"] = mutator()
        print(f'-- Added: "new_key_{self.seed} {o[f"new_key_{self.seed}"]}')
        return o

    def remove_kv(self,o):
        randkey = random.choice(list(o.keys()))
        print(f'-- Removed: {randkey} {o[randkey]}')
        del o[randkey]
        return o
    
    def mutate_type(self, o):
        # first choose field
        randkey = random.choice(list(o.keys()))
        # identify its type
        field_type = type(o[randkey])
        if field_type is int:
            o[randkey] = IntMutator().mutate(o[randkey])
        elif field_type is str:
            o[randkey] = StringMutator().mutate(o[randkey])
        elif field_type is float:
            o[randkey] = FloatMutator().mutate(o[randkey])
        elif field_type is list:
            # o[randkey] = StringMutator().mutate(o[randkey]) # TODO cause we haven;t done yey
            print("GRRRRRRRRRRRRR list not implemented. pls do")
        elif field_type is bool:
            o[randkey] = BooleanMutator().mutate(o[randkey])
        elif field_type is dict:
            o[randkey] = self.mutate(o[randkey])
        elif field_type is None:
            print("Null mutator goes brrrrrr (doesn't exist, pls implement???)")
        
        print(f'-- Mutated: {randkey} {o[randkey]}')

        return o

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
    
    