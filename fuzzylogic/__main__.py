try:
    from fuzzylogic import main
except ImportError:
    print('*' * 10 + '''
    Do not call this file directly, use ./main.py instead
    Call this file by executing it as a package with python3 -m fuzzylogic
''' + '*' * 10)
    exit(1)

main()
