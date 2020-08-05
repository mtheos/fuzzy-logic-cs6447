import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from .traceInfo import TraceInfo
os.environ['PWNLIB_SILENT'] = '1'  # suppresses ELF
# import pwn


class ThreadedRunner:
    _exit_codes_ = defaultdict(lambda: 'Something happened?')
    _exit_codes_[0] = 'Nope :('
    _exit_codes_[-6] = 'abort! :('
    _exit_codes_[-11] = 'Segfault! :)'
    _exit_codes_[134] = 'abort! :('
    _exit_codes_[139] = 'Segfault! :)'

    def __init__(self):
        self._executor = PoolExecutor(max_workers=os.cpu_count())
        self.architecture = None
        self._next_task = 0
        self._tasks = {}
        self._runs = 0

    def shutdown(self):
        self._executor.shutdown(wait=False)

    def is_done(self, task_id):
        task = self._tasks.get(task_id, None)
        if task is None:
            raise KeyError(f'{task_id} was requested but is not known')
        return task.future.done()

    def get_result(self, task_id):
        task = self._tasks.get(task_id, None)
        if task is None:
            raise KeyError(f'{task_id} was requested but is not known')
        if not task.future.done():
            raise BlockingIOError('Check is task is done with is_done(task_id) first')
        return task.code, task.input, task.trace_info

    def run_process(self, binary, _input):
        return self._run_process_(binary, _input)

    def parse_code(self, code):
        return self._exit_codes_[code]

    def _run_process_(self, binary, _input):
        # self._runs += 1
        # print(self._runs)
        if self.architecture is None:
            # self.architecture = pwn.ELF(binary).arch
            self.architecture = 'i386'
        task_id = self._next_task
        self._next_task += 1
        future = self._executor.submit(self._run_task_, binary, _input, task_id)
        self._tasks[task_id] = Task(future, _input)
        return task_id

    def _run_task_(self, binary, _input, task_id):
        if self.architecture != 'i386':
            code = os.system(f'{binary} >/dev/null <<\'EOF\'\n{_input}EOF')
            trace_data = []
        else:
            # if it is i386, use le qemu
            trace_file = f'/dev/shm/trace_{task_id}'
            # if self._runs < 100:
            #     code = os.system(f'qemu-i386 -d exec -D {trace_file} {binary} >/dev/null <<\'EOF\'\n{{}}EOF')
            # else:
            code = os.system(f'qemu-i386 -d exec -D {trace_file} {binary} >/dev/null <<\'EOF\'\n{_input}EOF')
            # TODO: see if we need to drop this to x00mb with multithreading
            max_file_size = int(1e9)  # if its bigger than this, dont bother
            fd = os.open(trace_file, os.O_RDONLY)
            trace_file_data = os.read(fd, max_file_size)
            os.close(fd)
            trace_data = self.get_trace(trace_file_data)
        # the return value from os.system is 2 bytes
        # the high byte is the exit code and the low byte is the signal (if any)
        # so >> 8 will get just the exit code
        # performance hit of shift right is 50% so check!
        if code != 0:
            code >>= 8
        self._tasks[task_id].code = code
        self._tasks[task_id].trace_info = TraceInfo(trace_data)

    @staticmethod
    def get_trace(file_data):
        file_data = file_data[file_data.find(b'Trace'):]
        # print('split = ', file_data.split(b']'))
        trace = list(map(lambda x: int(x[-8:], 16), file_data.split(b']')[:-1]))
        return trace


class Task:
    def __init__(self, future, _input):
        self.future = future
        self.input = _input
        self.trace_info = None
        self.code = None


def bench_executor(commands):
    print('executor start')
    runner = ThreadedRunner()
    task_ids = []
    for cmd in commands:
        task_ids.append(runner.run_process(cmd, ''))
    print('processes started')
    while len(task_ids) > 0:
        task_id = task_ids[0]
        if runner.is_done(task_id):
            task_ids.remove(task_id)
            code, _input, _ = runner.get_result(task_id)
            if code != 0:
                print(f'we did it reddit :) => {code} {runner.parse_code(code)}')
            else:
                print('nope :(')
    print('executor end')


def benchmark():
    cli = [
        'true',
        './seg'
    ]
    commands = [cli[i % 2] for i in range(5000)]
    bench_executor(commands)


if __name__ == '__main__':
    benchmark()
