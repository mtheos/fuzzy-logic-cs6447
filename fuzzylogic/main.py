#!/usr/bin/python
import sys
import os

def main(s):
    if len(sys.argv) != 3:
        print('Usage: <binary> <input>')
        exit(os.EX_USAGE)
    print(s)
    print(f'binary: {sys.argv[1]}')
    print(f'input: {sys.argv[2]}')
    exit(os.EX_OK)

if __name__ == '__main__':
	main('main.py was called directly')
