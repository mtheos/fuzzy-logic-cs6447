import os
# import re
# import pwn
# from subprocess import Popen, PIPE
from pwn import *
from collections import defaultdict
import datetime

class Runner:
    _exit_codes_ = defaultdict(lambda: 'Something happened?')
    _exit_codes_[0] = 'Nope :('
    _exit_codes_[-6] = 'Stack Smashing! :)'
    _exit_codes_[134] = 'Stack Smashing! :)'
    _exit_codes_[-11] = 'Segfault! :)'
    _exit_codes_[35584] = 'Segfault! :)'
    

    def __init__(self):
        self.architecture = ""

        #implement file in memory properly later if this is too slow
        self.TRACE_FILE = '/dev/shm/trace' 
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
        if (self.architecture == ""):
            #todo(theos, frances, aran): supress output from doing ELF(binary)
            self.architecture = ELF(binary).arch

        if (self.architecture != 'i386'):
            the_command = f'{binary} >/dev/null <<\'EOF\'\n{_input}EOF'
            code = os.system(the_command)
            filedata = []
        else:
            # if its i386, use le qemu
            the_command = f"qemu-i386 -d exec -D {self.TRACE_FILE} {binary} >/dev/null <<'EOF'\n{_input}EOF"
            code = os.system(the_command)
            f = os.open(self.TRACE_FILE, os.O_RDONLY)
            MAX_FILE_SIZE = int(1e9) #if its bigger than this, dont bother
            tracefile_data = os.read(f, MAX_FILE_SIZE)
            os.close(f)
            filedata = self.get_trace(tracefile_data)

        return PriorityInfo(filedata, code)

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

    def get_trace(self, filedata):
        filedata = filedata[filedata.find(b"Trace"):]
        # print("splitted = ", filedata.split(b"]"))
        trace = list(map(lambda x : int(x[-8:], 16), filedata.split(b"]")[:-1]))
        return trace

class PriorityInfo:
    def __init__(self, jumplist, code):
        self.jumps = jumplist
        self.return_code = code
        self.edges = {} # edges in the execution path
        for i in range(1, len(self.jumps)):
            if (self.jumps[i-1], self.jumps[i]) not in self.edges:
                self.edges[(self.jumps[i-1], self.jumps[i])] = 1
            else:
                self.edges[(self.jumps[i-1], self.jumps[i])] += 1

    def __lt__(self, other):
        return self.priority_function() < other.priority_function()

    def __repr__(self):
        return f'({self.jumps}) "{self.return_code}" idk lol'
    
    def __gt__(self, data2):
        return self.priority_function() > data2.priority_function()

    def __eq__(self, x):
        return self.__repr__() == x.__repr__()  # equality by value

    def __hash__(self):
        return self.__repr__().__hash__()

    def priority_function(self):
        return len(self.jumps)