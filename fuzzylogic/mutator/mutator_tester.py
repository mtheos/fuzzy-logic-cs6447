import sys
sys.path.append('../../')
__name__ = 'fuzzylogic.mutator.mutator_tester'
__package__ = 'fuzzylogic.mutator'
print(__name__)
print(__package__)

from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .boolean_mutator import BooleanMutator
from .complex_mutators import ListMutator, ObjectMutator

# string = "asdfghjkl"

# mut = StringMutator()
# final = string
# for i in range(0,15):
#     final = mut.mutate(final)
#     print(f"{i}: {final}")

# num = 246
# mut = FloatMutator()
# final = num
# for i in range(0,15):
#     final = mut.mutate(final)
#     print(f"{i}: {final}")

# result =  False
# mut = BooleanMutator()
# print(mut.mutate(result))

# dictionary = {"Arushi" : 22, "Anuradha" : 21, "Mani" : 21, "Haritha" : 21} 

# lol = ObjectMutator()
# print(f"== {dictionary} == ")
# mutation = dictionary
# for i in range(0,15):
#     mutation = lol.mutate(mutation)
#     print(f"{i}: {mutation}")

lis = [1, 2, 3]
l_mutator = ListMutator()
mutation = lis
for i in range(100):
    mutation = l_mutator.mutate(mutation)
    print(mutation)
