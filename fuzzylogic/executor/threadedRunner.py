import os
import distro
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor as PoolExecutor
from .traceInfo import TraceInfo
os.environ['PWNLIB_SILENT'] = '1'  # suppresses ELF
import pwn
# try:
#     import pwn
# except Exception:
#     class pwn:  # pwn fails to import if your TTY doesn't support curses (this is for debugging)
#         class ELF:
#             def __init__(self, binary):
#                 if 'xml3' in binary:
#                     self.arch = 'amd64'
#                 else:
#                     self.arch = 'i386'


class ThreadedRunner:
    _exit_codes_ = defaultdict(lambda: 'Something happened?')
    _exit_codes_[0] = 'Nope :('
    _exit_codes_[1] = 'Pranked :('
    _exit_codes_[-6] = 'abort! :('
    _exit_codes_[-11] = 'Segfault! :)'
    _exit_codes_[134] = 'abort! :('
    _exit_codes_[139] = 'Segfault! :)'
    _shutdown = False

    def __init__(self):
        # double the number of cores seems to be optimal, after this performance starts to drop off, tanking at 3x
        # memory footprint (driven by trace files) also plays a big role in performance. After 4GB on my machine performance drops sharply
        self._runs = 0
        self._tasks = {}
        self._next_task = 0
        self._has_stalled = False
        self._architecture = None
        self._num_workers = os.cpu_count() * 2  # Felt cute, might tweak later
        self._executor = PoolExecutor(max_workers=self._num_workers)

    def num_workers(self):
        return self._num_workers

    def shutdown(self, wait=False):
        self._shutdown = True
        self._executor.shutdown(wait)

    def clear_stalled(self):
        # stalled is called on 2 threads (reporting + work)
        # clearing it is separate so we don't miss any stalls
        self._has_stalled = False

    def stalled(self):
        stalled = self._has_stalled
        return stalled

    def is_done(self, task_id):
        task = self._tasks.get(task_id, None)
        if task is None:
            raise KeyError(f'{task_id} was requested but is not known')
        return task.done()

    def get_result(self, task_id):
        task = self._tasks.get(task_id, None)
        if task is None:
            raise KeyError(f'{task_id} was requested but is not known')
        if not task.done():
            raise BlockingIOError('Check is task is done with is_done(task_id) first')
        del self._tasks[task_id]
        return task.result()

    def run_process(self, binary, _input):
        return self._run_process_(binary, _input)

    def parse_code(self, code):
        return self._exit_codes_[code]

    def get_arch(self):
        return self._architecture

    def _run_process_(self, binary, _input):
        if self._architecture is None:
            self._architecture = pwn.ELF(binary).arch
        if len(self._tasks) == 0:
            self._has_stalled = True
        task_id = self._next_task
        self._next_task += 1
        future = self._executor.submit(self._run_task_, binary, _input, task_id, self._architecture)
        self._tasks[task_id] = future
        return task_id

    @classmethod
    def _run_task_(cls, binary, _input, task_id, architecture):
        # Running qemu to clear jobs is (comparatively) slow if we're just shutting down.
        # Return value doesn't matter either as the main thread won't look at it anymore
        if cls._shutdown:
            return
        input_file = f'/dev/shm/input_{task_id}'
        trace_file = f'/dev/shm/trace_{task_id}'
        fd = os.open(input_file, os.O_WRONLY | os.O_CREAT, 0o644)
        try:
            os.write(fd, _input.encode())
        except UnicodeEncodeError:
            os.close(fd)
            os.remove(input_file)
            return -1, _input, TraceInfo([], architecture)
        os.close(fd)
        run_binary = f'{binary} > /dev/null 2> /dev/null < {input_file}'
        if architecture not in ['i386', 'amd64']:
            code = os.system(run_binary)
            trace_data = []
        else:
            if architecture == 'i386':
                qemu = 'qemu-i386'
            else:  # 'amd64'
                qemu = 'qemu-x86_64'
            code = os.system(f'{qemu} -d exec -D {trace_file} {run_binary}')
            max_file_size = int(1.5e7)  # 95% of traces are <= 15mb
            fd = os.open(trace_file, os.O_RDONLY)
            trace_file_data = os.read(fd, max_file_size)
            os.close(fd)
            os.remove(trace_file)
            trace_data = cls._get_trace_(trace_file_data, architecture)
        os.remove(input_file)
        # the return value from os.system is 2 bytes
        # the high byte is the exit code and the low byte is the signal (if any)
        # so >> 8 will get just the exit code
        # performance hit of shift right is 50% so check!
        if code != 0:
            code >>= 8
        return code, _input, TraceInfo(trace_data, architecture)

    @classmethod
    def _get_trace_(cls, file_data, architecture):
        # qemu returns a differently formatted trace file in 20.04... fml
        if distro.version()[:2] == '20' and architecture == 'amd64':
            return cls._get_trace_20_04_special_(file_data)
        return cls._get_trace_rest_(file_data, architecture)

    @staticmethod
    def _get_trace_rest_(file_data, architecture):
        # if you got this far and your binary wasn't i386 or amd64, you're probably already having a bad day
        if architecture == 'amd64':
            address_size = 16
        else:
            address_size = 8
        file_data = file_data[file_data.find(b'Trace'):]
        trace = list(map(lambda x: int(x[-address_size:], 0x10), file_data.split(b']')[:-1]))
        return trace

    @staticmethod
    def _get_trace_20_04_special_(file_data):
        # special implementation only for 64 bit on Ubuntu 20.04
        address_size = 16
        file_data = file_data[file_data.find(b'Trace'):]
        trace = []
        for line in file_data.split(b']')[:-1]:
            line = line[line.index(b'[') + 1:]
            if len(line) == 16:
                trace.append(line)
            else:
                trace.append(line[-(address_size + 9):-9])
        return list(map(lambda x: int(x, 0x10), trace))
