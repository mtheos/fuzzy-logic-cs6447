import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor


class ThreadedRunner:
    _exit_codes_ = defaultdict(lambda: 'Something happened?')
    _exit_codes_[0] = 'Nope :('
    _exit_codes_[-6] = 'abort! :('
    _exit_codes_[-11] = 'Segfault! :)'
    _exit_codes_[134] = 'abort! :('
    _exit_codes_[139] = 'Segfault! :)'

    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=os.cpu_count())
        self._next_task = 0
        self._tasks = {}

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
        return task.code, task.input

    def run_process(self, binary, _input):
        return self._run_process_(binary, _input)
        # return self._run_process_fake_(binary, _input)

    def parse_code(self, code):
        return self._exit_codes_[code]

    def _run_process_(self, binary, _input):
        task_id = self._next_task
        self._next_task += 1
        future = self._executor.submit(self._run_task_, binary, _input, task_id)
        self._tasks[task_id] = Task(future, _input)
        return task_id

    def _run_task_(self, binary, _input, task_id):
        code = os.system(f'{binary} >/dev/null <<\'EOF\'\n{_input}EOF')
        # the return value from os.system is 2 bytes
        # the high byte is the exit code and the low byte is the signal (if any)
        # so >> 8 will get just the exit code
        # performance hit of shift right is 50% so check!
        if code != 0:
            code >>= 8
        self._tasks[task_id].code = code

    def _run_process_fake_(self, binary, _input):
        task_id = self._next_task
        self._next_task += 1
        future = self._executor.submit(self._run_task_fake_, binary, _input, task_id)
        self._tasks[task_id] = Task(future, _input)
        return task_id

    def _run_task_fake_(self, binary, _input, task_id):
        os.system(f'{binary} >/dev/null <<\'EOF\'\n{_input}EOF')
        self._tasks[task_id].code = 0


class Task:
    def __init__(self, future, _input):
        self.future = future
        self.input = _input
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
            code, _input = runner.get_result(task_id)
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
