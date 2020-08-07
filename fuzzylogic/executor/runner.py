import os
from collections import defaultdict
from .traceInfo import TraceInfo
os.environ['PWNLIB_SILENT'] = '1'  # suppresses ELF output
try:
    import pwn
except Exception:
    class pwn:  # pwn fails to import if your TTY doesn't support curses
        class ELF:
            def __init__(self, binary):
                if 'xml3' in binary:
                    self.arch = 'amd64'
                else:
                    self.arch = 'i386'


class Runner:
    _exit_codes_ = defaultdict(lambda: 'Something happened?')
    _exit_codes_[0] = 'Nope :('
    _exit_codes_[-6] = 'abort! :('
    _exit_codes_[-11] = 'Segfault! :)'
    _exit_codes_[134] = 'abort! :('
    _exit_codes_[35584] = 'Segfault! :)'

    def __init__(self):
        self._architecture = None
        self._trace_file = '/dev/shm/trace'  # implement file in memory properly later if this is too slow

    def run_process(self, binary, _input):
        return self._run_process_(binary, _input)
        # return self._run_process_fake_(binary, _input)

    def parse_code(self, code):
        return self._exit_codes_[code]

    def get_arch(self):
        return self._architecture

    def _run_process_(self, binary, _input):
        if self._architecture is None:
            self._architecture = pwn.ELF(binary).arch

        run_binary = f'{binary} >/dev/null 2>/dev/null <<\'EOF\'\n{_input}EOF'
        if self._architecture not in ['i386', 'amd64']:
            code = os.system(run_binary)
            trace_data = []
        else:
            if self._architecture == 'i386':
                qemu = 'qemu-i386'
            elif self._architecture == 'amd64':
                qemu = 'qemu-x86_64'
            else:
                raise RuntimeError('If you got this error, you spelt i386 or amd64 wrong :)')
            max_file_size = int(1e9)  # if its bigger than this, dont bother
            code = os.system(f'{qemu} -d exec -D {self._trace_file} {run_binary}')
            fd = os.open(self._trace_file, os.O_RDONLY)
            trace_file_data = os.read(fd, max_file_size)
            os.close(fd)
            os.remove(self._trace_file)
            trace_data = self.get_trace(trace_file_data)
        return code, _input, TraceInfo(trace_data)

    def _run_process_fake_(self, binary, _input):
        self._run_process_(binary, _input)
        return 0

    @staticmethod
    def get_trace(file_data, architecture):
        # if you got this far and your binary wasn't i386 or amd64, you're probably already having a bad day
        if architecture == 'amd64':
            address_size = 16
        else:
            address_size = 8
        file_data = file_data[file_data.find(b'Trace'):]
        trace = list(map(lambda x: int(x[-address_size:], 0x10), file_data.split(b']')[:-1]))
        return trace
