import os
from collections import defaultdict
from .traceInfo import TraceInfo
os.environ['PWNLIB_SILENT'] = '1'  # suppresses ELF output
# import pwn


class Runner:
    _exit_codes_ = defaultdict(lambda: 'Something happened?')
    _exit_codes_[0] = 'Nope :('
    _exit_codes_[-6] = 'abort! :('
    _exit_codes_[-11] = 'Segfault! :)'
    _exit_codes_[134] = 'abort! :('
    _exit_codes_[35584] = 'Segfault! :)'

    def __init__(self):
        self.architecture = None
        self.TRACE_FILE = '/dev/shm/trace'  # implement file in memory properly later if this is too slow

    def run_process(self, binary, _input):
        return self._run_process_(binary, _input)
        # return self._run_process_fake_(binary, _input)

    def parse_code(self, code):
        return self._exit_codes_[code]

    def _run_process_(self, binary, _input):
        if self.architecture is None:
            # self.architecture = pwn.ELF(binary).arch
            self.architecture = 'i386'

        if self.architecture != 'i386':
            # Put EOF in quotes and you don't need to escape anything
            the_command = f'{binary} >/dev/null <<\'EOF\'\n{_input}EOF'
            code = os.system(the_command)
            file_data = []
        else:
            # if its i386, use le qemu
            the_command = f'qemu-i386 -d exec -D {self.TRACE_FILE} {binary} >/dev/null <<\'EOF\'\n{_input}EOF'
            code = os.system(the_command)
            max_file_size = int(1e9)  # if its bigger than this, dont bother
            fd = os.open(self.TRACE_FILE, os.O_RDONLY)
            trace_file_data = os.read(fd, max_file_size)
            os.close(fd)
            file_data = self.get_trace(trace_file_data)
        return code, _input, TraceInfo(file_data)

    def _run_process_fake_(self, binary, _input):
        self._run_process_(binary, _input)
        return 0

    @staticmethod
    def get_trace(file_data):
        file_data = file_data[file_data.find(b'Trace'):]
        # print('split = ', file_data.split(b']'))
        trace = list(map(lambda x: int(x[-8:], 16), file_data.split(b']')[:-1]))
        return trace
