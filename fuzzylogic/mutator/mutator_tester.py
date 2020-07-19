import sys
import json
import random
sys.path.append('../../')
__name__ = 'fuzzylogic.mutator.mutator_tester'
__package__ = 'fuzzylogic.mutator'
print(__name__)
print(__package__)

from .int_mutator import IntMutator
from .float_mutator import FloatMutator
from .string_mutator import StringMutator
from .boolean_mutator import BooleanMutator
from .csv_row_mutator import CsvRowMutator
from .complex_mutators import ListMutator, ObjectMutator

# mut = StringMutator()
# print(mut.meme_mutation(5.0))
# string = "hello"
# for i in range(16):
#     string = mut.mutate(string)
#     print(string)

mut = CsvRowMutator()
csv = [[1,2,3],['lol','yay',4]]
print(mut.mutate(csv,0))

# print("---- Turn right")
# print("---- Another comment")

# print(1+1)
# print("What's your name?")

# name = input()

# print("Hi "+ name)
# print("how was your day")
# day = input()

# print(string)

# infinity = float('Infinity')
# print(type(infinity))
# # infinity -= 100000
# print(infinity)

# lol = {"wow":infinity}

# lol2 = json.dumps(lol)

# print(lol2)

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

# dictionary = {"Arushi" : 'lolz', "Anuradha" : 21, "Mani" : 21, "Haritha" : 21} 

# lol = ObjectMutator()

# print(f"== {dictionary} == ")
# mutation = dictionary
# for i in range(0,15):
#     mutation = lol.mutate(mutation)
#     print(f"{i}: {mutation}")

# lis = [1, 2, 3]
# l_mutator = ListMutator()
# mutation = lis
# for i in range(10):
#     mutation = l_mutator.mutate(mutation)
#     print(mutation)
