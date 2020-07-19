import os
# import re
# import pwn
# from subprocess import Popen, PIPE
from collections import defaultdict


class Runner:
    _exit_codes_ = defaultdict(lambda: 'Something happened?')
    _exit_codes_[0] = 'Nope :('
    _exit_codes_[-6] = 'Stack Smashing! :)'
    _exit_codes_[134] = 'Stack Smashing! :)'
    _exit_codes_[-11] = 'Segfault! :)'
    _exit_codes_[35584] = 'Segfault! :)'

    def __init__(self):
        pass

    def run_process(self, binary, _input, fake=False):
        if fake:
            return self._run_process_fake_(binary, _input)
        return self._run_process_cmd_(binary, _input)
        # return self._run_process_p_open_(binary, _input)
        # return self._run_process_pwn_tools_(binary, _input)

    def _run_process_fake_(self, binary, _input):
        self._run_process_cmd_(binary, _input)
        return 0

    def _run_process_cmd_(self, binary, _input):
        # _input = re.sub('(!|\$|#|&|\'|\(|\)|\||<|>|`|\\|\|;)', r"\\\1", _input)
        # Put EOF in quotes and you don't need to escape anything
        code = os.system(f'{binary} >/dev/null <<\'EOF\'\n{_input}EOF')
        return code

    # def _run_process_pwn_tools_(self, binary, _input):
    #     p = pwn.process(binary)
    #     p.send(_input)
    #     p.wait()
    #     code = p.poll()
    #     return code
    #
    # def _run_process_p_open_(self, binary, _input):
    #     p = Popen(binary, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    #     p.communicate(_input.encode())
    #     code = p.wait()
    #     return code

    def parse_code(self, code):
        return self._exit_codes_[code]
