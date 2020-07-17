from string_mutator import *

string = "asdfghjkl"

mut = StringMutator()
final = string
for i in range(0,15):
    final = mut.mutate(final)
    print(f"{i}: {final}")

