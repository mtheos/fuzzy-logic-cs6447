from string_mutator import *
from int_mutator import IntMutator
from float_mutator import *
from boolean_mutator import *
from object_mutator import *

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

dictionary = {"Arushi" : 22, "Anuradha" : 21, "Mani" : 21, "Haritha" : 21} 

lol = ObjectMutator()
print(f"== {dictionary} == ")
mutation = dictionary
for i in range(0,15):
    mutation = lol.mutate(mutation)
    print(f"{i}: {mutation}")
