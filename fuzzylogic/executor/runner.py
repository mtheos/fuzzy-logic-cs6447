from subprocess import Popen, PIPE
from collections import defaultdict
# from pwn import *

class Runner:
    _exit_codes_ = defaultdict(lambda: 'Nope :(')
    _exit_codes_[-6] = 'Stack Smashing! :)'
    _exit_codes_[-11] = 'Segfault! :)'

    def __init__(self):
        pass

    def run_process(self, binary, _input):
        return self.run_process_p_open(binary, _input)
        # return self.run_process_pwn_tools(binary, _input)

    def run_process_pwn_tools(self, binary, _input):
        p = process(binary)
        p.send(_input)
        p.wait()
        code = p.poll()
        return code

    def run_process_p_open(self, binary, _input):
        p = Popen(binary, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(_input.encode())
        code = p.wait()
        return code

    def parse_code(self, code):
        return self._exit_codes_[code]
