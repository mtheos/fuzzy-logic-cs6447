import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor as PoolExecutor
from .traceInfo import TraceInfo
os.environ['PWNLIB_SILENT'] = '1'  # suppresses ELF
try:
    import pwn
except Exception:
    class pwn:
        class ELF:
            def __init__(self, binary):
                self.arch = 'i386'


class ThreadedRunner:
    _exit_codes_ = defaultdict(lambda: 'Something happened?')
    _exit_codes_[0] = 'Nope :('
    _exit_codes_[-6] = 'abort! :('
    _exit_codes_[-11] = 'Segfault! :)'
    _exit_codes_[134] = 'abort! :('
    _exit_codes_[139] = 'Segfault! :)'

    def __init__(self):
        # double the number of cores seems to be optimal, after this performance starts to drop off, tanking at 3x
        # memory footprint (driven by trace files) also plays a big role in performance. After 4GB on my machine performance drops sharply
        self._num_workers = os.cpu_count() * 2  # Felt cute, might tweak later
        self._executor = PoolExecutor(max_workers=self._num_workers)
        self.architecture = None
        self._next_task = 0
        self._tasks = {}
        self._runs = 0

    def num_workers(self):
        return self._num_workers

    def shutdown(self):
        self._executor.shutdown(wait=False)

    def stalled(self):
        # If you didn't want me using private members you should have made it public
        # return self._executor._work_queue.qsize() == 0
        return self._executor._queue_count == 0

    def is_done(self, task_id):
        task = self._tasks.get(task_id, None)
        if task is None:
            raise KeyError(f'{task_id} was requested but is not known')
        # return task.future.done()
        return task.done()

    def get_result(self, task_id):
        task = self._tasks.get(task_id, None)
        if task is None:
            raise KeyError(f'{task_id} was requested but is not known')
        # if not task.future.done():
        if not task.done():
            raise BlockingIOError('Check is task is done with is_done(task_id) first')
        # return task.code, task.input, task.trace_info
        # return task.future.result()
        return task.result()

    def run_process(self, binary, _input):
        return self._run_process_(binary, _input)

    def parse_code(self, code):
        return self._exit_codes_[code]

    def _run_process_(self, binary, _input):
        if self.architecture is None:
            self.architecture = pwn.ELF(binary).arch
            # self.architecture = ''
        task_id = self._next_task
        self._next_task += 1
        future = self._executor.submit(self._run_task_, binary, _input, task_id, self.architecture)
        # self._tasks[task_id] = Task(future, _input)
        self._tasks[task_id] = future
        return task_id

    @classmethod
    def _run_task_(cls, binary, _input, task_id, architecture):
        if architecture != 'i386':
            code = os.system(f'{binary} >/dev/null <<\'EOF\'\n{_input}EOF')
            trace_data = []
        else:
            # if it is i386, use le qemu
            trace_file = f'/dev/shm/trace_{task_id}'
            code = os.system(f'qemu-i386 -d exec -D {trace_file} {binary} >/dev/null <<\'EOF\'\n{_input}EOF')
            # TODO: see if we need to drop this to x00mb with multithreading
            max_file_size = int(1e9)  # if its bigger than this, dont bother
            fd = os.open(trace_file, os.O_RDONLY)
            trace_file_data = os.read(fd, max_file_size)
            os.close(fd)
            os.remove(trace_file)
            trace_data = cls.get_trace(trace_file_data)
        # the return value from os.system is 2 bytes
        # the high byte is the exit code and the low byte is the signal (if any)
        # so >> 8 will get just the exit code
        # performance hit of shift right is 50% so check!
        if code != 0:
            code >>= 8
        # self._tasks[task_id].code = code
        # self._tasks[task_id].trace_info = TraceInfo(trace_data)
        return code, _input, TraceInfo(trace_data)

    @staticmethod
    def get_trace(file_data):
        file_data = file_data[file_data.find(b'Trace'):]
        # print('split = ', file_data.split(b']'))
        trace = list(map(lambda x: int(x[-8:], 16), file_data.split(b']')[:-1]))
        return trace


# class Task:
#     def __init__(self, future, _input):
#         self.future = future
#         self.input = _input
#         self.trace_info = None
#         self.code = None
