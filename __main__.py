#!/usr/bin/python3

# This just calls the src folder as a module
try:
    from fuzzylogic import main
except ModuleNotFoundError:
    try:
        from .fuzzylogic import main
    except ModuleNotFoundError:
        print('''
    Fatal: Failed to import main
''')
        exit(1)

main()
