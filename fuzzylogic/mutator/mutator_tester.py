from string_mutator import *
from int_mutator import IntMutator

# string = "asdfghjkl"

# mut = StringMutator()
# final = string
# for i in range(0,15):
#     final = mut.mutate(final)
#     print(f"{i}: {final}")

num = 246
mut = IntMutator()
final = num
for i in range(0,15):
    final = mut.mutate(final)
    print(f"{i}: {final}")