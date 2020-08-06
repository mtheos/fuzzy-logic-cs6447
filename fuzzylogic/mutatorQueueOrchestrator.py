import os
import time
from threading import Thread, currentThread
from queue import PriorityQueue
from queue import Queue
import resource


class RunOrchestrator:
    def __init__(self, runner, fuzzer_inputs, running_tasks, limits):
        self._runs = 0
        self._runner = runner
        self._fuzzer_inputs = fuzzer_inputs
        self._running_tasks = running_tasks
        self._limits = limits

    def total_runs(self):
        return self._runs

    def run_new_inputs(self, binary):
        # too many binaries is inefficient as new cases could have better priority
        while self.has_inputs() and self.running() < self._limits['MAX_RUNNING_INPUTS']:
            self._runs += 1
            _input = self._fuzzer_inputs.get().data
            self._running_tasks.put(self._runner.run_process(binary, _input))

    def has_inputs(self):
        return not self._fuzzer_inputs.empty()

    def running(self):
        return self._running_tasks.qsize()

    def stalled(self):
        return self._runner.stalled()


class CheckOrchestrator:
    def __init__(self, runner, fuzzer_inputs, running_tasks, to_mutate, seen, limits):
        self._seen = seen
        self._runner = runner
        self._final_code = None
        self._final_input = None
        self._to_mutate = to_mutate
        self._fuzzer_inputs = fuzzer_inputs
        self._running_tasks = running_tasks
        self._limits = limits

    def final_result(self):
        return self._final_code, self._final_input

    def check_finished_inputs(self):
        loop_check = None
        # If there are only a few tasks left (and we have more to run) stop early and queue more and don't stall the runner
        while not self._running_tasks.empty() and (self.running() > self._limits['MIN_RUNNING_INPUTS'] or not self.has_inputs()):
            task_id = self._running_tasks.get()
            if not self._runner.is_done(task_id):  # If the task is not complete put it back in the queue
                self._running_tasks.put(task_id)
                if loop_check is not None and loop_check == task_id:
                    break  # looped back to first thing we put back in
                if loop_check is None:
                    loop_check = task_id  # first id is the loop check
                continue
            code, _input, trace_info = self._runner.get_result(task_id)
            if code != 0:
                self._final_input = _input
                self._final_code = code
            self._seen[_input] = trace_info
            self._to_mutate.put(_input)

    def has_inputs(self):
        return not self._fuzzer_inputs.empty()

    def running(self):
        return self._running_tasks.qsize()


class MutateOrchestrator:
    def __init__(self, mutator, fuzzer_inputs, to_mutate, seen, distance, prev, limits):
        self._seen = seen
        self._prev = prev
        self._mutator = mutator
        self._distance = distance
        self._to_mutate = to_mutate
        self._fuzzer_inputs = fuzzer_inputs
        self._limits = limits

    def _put_(self, _input, priority, previous, distance):
        self._fuzzer_inputs.put(QueueItem(_input, priority))
        self._prev[_input] = previous
        self._distance[_input] = distance

    def create_more_inputs(self):
        # creating inputs is memory and time expensive O(n^2), pause creating inputs if we have a lot ready to run
        if self.awaiting_fuzzing() > self._limits['MIN_QUEUED_INPUTS']:
            return
        while not self._to_mutate.empty() and self.awaiting_fuzzing() < self._limits['MAX_QUEUED_INPUTS']:
            _input = self._to_mutate.get()
            trace_info = self._seen[_input]
            for mutation in self._mutator.mutate(_input):
                if mutation not in self._seen:
                    distance = self._distance[_input] + 1
                    priority = self._priority_function_(mutation, distance, trace_info)
                    # print(f'queued: {self._fuzzer_inputs.qsize()}, Running: {self.running()} priority {priority}')
                    self._put_(_input=mutation, priority=priority, previous=_input, distance=distance)

    # return negative weighting. (lower is higher priority)
    def _priority_function_(self, _input, distance, trace_info):
        # calculate the unique discovery of a block bonus
        if _input in self._prev:
            prev_jumps = set(self._seen[self._prev[_input]].jumps())
        else:
            prev_jumps = set()
        unique_discovery = 0
        for j in trace_info.jumps():
            if j not in prev_jumps:
                unique_discovery = 15000
                break
        return -1/(distance+15)*(len(trace_info.jumps()) + unique_discovery)

    def awaiting_fuzzing(self):
        return self._fuzzer_inputs.qsize()

    def stalled(self):
        return self.awaiting_fuzzing() == 0


class FuzzOrchestrator:
    def __init__(self, mutator, runner):
        self._seen = dict()
        self._prev = dict()
        self._distance = dict()
        self._runner = runner
        self._mutator = mutator
        self._to_mutate = Queue()
        self._running_tasks = Queue()
        self._fuzzer_inputs = PriorityQueue()
        self._limits = {
            'MIN_RUNNING_INPUTS': runner.num_workers() * 2,
            'MAX_RUNNING_INPUTS': runner.num_workers() * 4,
            'MIN_QUEUED_INPUTS': runner.num_workers() * 3,
            'MAX_QUEUED_INPUTS': runner.num_workers() * 6
        }
        self._runOrchestrator = RunOrchestrator(runner, self._fuzzer_inputs, self._running_tasks, self._limits)
        self._checkOrchestrator = CheckOrchestrator(runner, self._fuzzer_inputs, self._running_tasks, self._to_mutate, self._seen, self._limits)
        self._mutateOrchestrator = MutateOrchestrator(mutator, self._fuzzer_inputs, self._to_mutate, self._seen, self._distance, self._prev,
                                                      self._limits)

    def put(self, _input, priority, previous=None, distance=0):
        self._fuzzer_inputs.put(QueueItem(_input, priority))
        self._prev[_input] = previous
        self._distance[_input] = distance

    def final_result(self):
        return (*self._checkOrchestrator.final_result(), self._runOrchestrator.total_runs())

    def print_stats(self):
        while True:
            print(f'\033[{2};{0}H')
            console = 'Threaded Fuzzer\n'
            console += f'Total attempts : {self._runOrchestrator.total_runs()}\n'
            console += f'Worker Count   : {self._runner.num_workers()}\n'
            console += f'Running Tasks  : {self._runOrchestrator.running()}\n'
            console += f'Queued Inputs  : {self._fuzzer_inputs.qsize()}\n'
            console += f'Awaiting Fuzz  : {self._mutateOrchestrator.awaiting_fuzzing()}\n'
            console += f'Task Q Size    : {self._limits["MIN_RUNNING_INPUTS"]} - {self._limits["MAX_RUNNING_INPUTS"]}\n'
            console += f'Fuzz Q Size    : {self._limits["MIN_QUEUED_INPUTS"]} - {self._limits["MAX_QUEUED_INPUTS"]}\n'
            console += f'Runner         : {"stalled!" if self._runOrchestrator.stalled() else "OK"}\n'
            console += f'Mutator        : {"stalled!" if self._mutateOrchestrator.stalled() else "OK"}\n'
            console += f'resource_rss   : {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000}MB\n'
            print(console)
            if currentThread().name != 'stat-printer':
                break
            time.sleep(1)
            if self._checkOrchestrator.final_result()[0] is not None:
                break

    def run(self, binary):
        os.system('clear')
        Thread(target=self.print_stats, name='stat-printer').start()
        delay = 0
        while True:
            if delay > 3:
                if self._runOrchestrator.stalled():
                    self._limits['MIN_RUNNING_INPUTS'] = min(int(self._limits['MIN_RUNNING_INPUTS'] * 1.2) + 1, 100)
                    self._limits['MAX_RUNNING_INPUTS'] = min(int(self._limits['MAX_RUNNING_INPUTS'] * 1.2) + 1, 1000)
                    if self._mutateOrchestrator.stalled():
                        self._limits['MIN_QUEUED_INPUTS'] = min(int(self._limits['MIN_QUEUED_INPUTS'] * 1.2) + 1, 200)
                        self._limits['MAX_QUEUED_INPUTS'] = min(int(self._limits['MAX_QUEUED_INPUTS'] * 1.2) + 1, 2000)
            else:
                delay += 1
            self._runOrchestrator.run_new_inputs(binary)
            self._checkOrchestrator.check_finished_inputs()
            self._mutateOrchestrator.create_more_inputs()
            # time.sleep(0.1)
            # self._cull_queued_()  # maybe
            if self._runOrchestrator.total_runs() > 20000:
                self._checkOrchestrator._final_code = 1234
                self._checkOrchestrator._final_input = 'hard exit'
            if self._checkOrchestrator.final_result()[0] is not None:
                self._runner.shutdown()
                break

    def __repr__(self):
        return f'Inputs waiting to run: {len(self._fuzzer_inputs.queue)} | Inputs running: {len(self._running_tasks.queue)}'











# class MutatorQueueOrchestrator:
#     def __init__(self, mutator, runner):
#         self.MIN_RUNNING_INPUTS = runner.num_workers() * 2
#         self.MAX_RUNNING_INPUTS = runner.num_workers() * 5
#         self.MIN_QUEUED_INPUTS = runner.num_workers() * 5
#         self.MAX_QUEUED_INPUTS = runner.num_workers() * 10
#         self._mutator = mutator
#         self._runner = runner
#         self._fuzzer_inputs = PriorityQueue()
#         self._to_mutate = Queue()
#         self._running_tasks = Queue()
#         self._seen = dict()
#         self._distance = dict()
#         self._prev = dict()
#         self._runs = 0
#         self._final_input = None
#         self._final_code = None
#
#     def final_result(self):
#         return self._final_code, self._final_input, self._runs
#
#     def put(self, _input, priority, previous=None, distance=0):
#         self._fuzzer_inputs.put(QueueItem(_input, priority))
#         self._prev[_input] = previous
#         self._distance[_input] = distance
#
#     def get(self):
#         to_fuzz = self._fuzzer_inputs.get()
#         return to_fuzz.data
#
#     def print_stats(self):
#         while True:
#             print(f'\033[{3};{0}H')
#             console = 'Threaded Fuzzer\n'
#             console += f'Total attempts : {self._runs}\n'
#             console += f'Worker Count   : {self._runner.num_workers()}\n'
#             console += f'Running tasks  : {self.running()}\n'
#             console += f'Queued inputs  : {self._fuzzer_inputs.qsize()}\n'
#             console += f'Awaiting Fuzz  : {self.awaiting_mutation()}'
#             print(console)
#             if currentThread().name != 'stat-printer':
#                 break
#             time.sleep(1)
#             if self._final_code:
#                 break
#
#     def run(self, binary):
#         os.system('clear')
#         Thread(target=self.print_stats, name='stat-printer').start()
#         while True:
#             # self.print_stats()
#             self._run_new_inputs_(binary)
#             self._check_finished_inputs_()
#             self._create_more_inputs_()
#             # self._cull_queued_()  # maybe
#             if self._final_code:
#                 self._runner.shutdown()
#                 break
#
#     def _run_new_inputs_(self, binary):
#         # too many binaries is inefficient as new cases could have better priority
#         while self.has_inputs() and self.running() < self.MAX_RUNNING_INPUTS:
#             self._runs += 1
#             _input = self.get()
#             self._running_tasks.put(self._runner.run_process(binary, _input))
#
#     def _check_finished_inputs_(self):
#         loop_check = None
#         # If there are only a few tasks left (and we have more to run) stop early and queue more and don't stall the runner
#         while not self._running_tasks.empty() and (self.running() > self.MIN_RUNNING_INPUTS or not self.has_inputs()):
#             task_id = self._running_tasks.get()
#             if not self._runner.is_done(task_id):  # If the task is not complete put it back in the queue
#                 self._running_tasks.put(task_id)
#                 if loop_check is not None and loop_check == task_id:
#                     break  # looped back to first thing we put back in
#                 if loop_check is None:
#                     loop_check = task_id  # first id is the loop check
#                 continue
#             code, _input, trace_info = self._runner.get_result(task_id)
#             if code != 0:
#                 self._final_input = _input
#                 self._final_code = code
#                 return
#             self._seen[_input] = trace_info
#             self._to_mutate.put(_input)
#
#     def _create_more_inputs_(self):
#         # creating inputs is memory and time expensive O(n^2), pause creating inputs if we have a lot ready to run
#         if self.awaiting_fuzzing() > self.MIN_QUEUED_INPUTS:
#             return
#         while not self._to_mutate.empty() and self.awaiting_fuzzing() < self.MAX_QUEUED_INPUTS:
#             _input = self._to_mutate.get()
#             trace_info = self._seen[_input]
#             for mutation in self._mutator.mutate(_input):
#                 if mutation not in self._seen:
#                     # self._prev[mutation] = _input
#                     distance = self._distance[_input] + 1
#                     priority = self._priority_function_(mutation, distance, trace_info)
#                     # print(f'queued: {self._fuzzer_inputs.qsize()}, Running: {self.running()} priority {priority}')
#                     self.put(_input=mutation, priority=priority, previous=_input, distance=distance)
#
#     # return negative weighting. (lower is higher priority)
#     def _priority_function_(self, _input, distance, trace_info):
#         # calculate the unique discovery of a block bonus
#         if _input in self._prev:
#             prev_jumps = set(self._seen[self._prev[_input]].jumps())
#         else:
#             prev_jumps = set()
#         unique_discovery = 0
#         for j in trace_info.jumps():
#             if j not in prev_jumps:
#                 unique_discovery = 15000
#                 break
#         return -1/(distance+15)*(len(trace_info.jumps()) + unique_discovery)
#
#     def has_inputs(self):
#         return not self._fuzzer_inputs.empty()
#
#     def awaiting_fuzzing(self):
#         return self._fuzzer_inputs.qsize()
#
#     def running(self):
#         return self._running_tasks.qsize()
#
#     def awaiting_mutation(self):
#         return self._to_mutate.qsize()
#
#     def __repr__(self):
#         return f'Inputs waiting to run: {len(self._fuzzer_inputs.queue)} | Inputs running: {len(self._running_tasks.queue)}'


class QueueItem:
    def __init__(self, data, priority):
        self.data = data
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __gt__(self, other):
        return self.priority > other.priority

    def __eq__(self, other):
        return self.priority == other.priority  # equality by value

    def __hash__(self):
        return self.__repr__().__hash__()
