#!/usr/bin/python3
import sys
import os
try:
    from fuzzylogic import fuzzer
except ModuleNotFoundError:
    sys.path.append('.')
    from fuzzylogic import fuzzer


def main():
    if len(sys.argv) != 3:
        print('Usage: <binary> <input>')
        exit(os.EX_USAGE)
    fuzzer.fuzz(sys.argv[1], sys.argv[2])
    exit(os.EX_OK)


if __name__ == '__main__':
    main()
