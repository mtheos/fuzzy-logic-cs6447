import os
import time
from threading import Thread
from queue import PriorityQueue
from queue import Queue
import resource
from .strategy import Strategy

class FuzzOrchestrator:
    def __init__(self, mutator, runner):
        self._seen = dict()
        self._prev = dict()
        self._distance = dict()
        self._runner = runner
        self._mutator = mutator
        self._to_mutate = Queue()
        self._stat_printer = None
        self._running_tasks = Queue()
        self._fuzzer_inputs = PriorityQueue()
        self._limits = {
            'MIN_RUNNING_INPUTS': runner.num_workers() * 2,
            'MAX_RUNNING_INPUTS': runner.num_workers() * 4,
            'MIN_QUEUED_INPUTS': runner.num_workers() * 3,
            'MAX_QUEUED_INPUTS': runner.num_workers() * 6,
            'MEMORY_LIMIT': 4000
        }
        self._runOrchestrator = RunOrchestrator(runner, self._fuzzer_inputs, self._running_tasks, self._limits)
        self._checkOrchestrator = CheckOrchestrator(runner, self._fuzzer_inputs, self._running_tasks, self._to_mutate, self._seen, self._limits)
        self._mutateOrchestrator = MutateOrchestrator(mutator, self._fuzzer_inputs, self._to_mutate, self._seen, self._distance, self._prev,
                                                      self._limits)

    def put(self, _input, priority, previous=None, distance=0):
        self._fuzzer_inputs.put(QueueItem(_input, priority))
        self._prev[_input] = previous
        self._distance[_input] = distance

    @staticmethod
    def _get_memory_usage_mb_():
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000

    def final_result(self):
        return (*self._checkOrchestrator.final_result(), self._runOrchestrator.total_runs())

    def _print_stats_(self):
        while True:
            print(f'\033[{2};{0}H')
            console = ' Fuzzy-Logic-6447 - Our logic is fuzzy but our minds are sharp\n\n'
            console += f' Total attempts : {self._runOrchestrator.total_runs()}\n'
            console += f' Worker Count   : {self._runner.num_workers()}\n'
            console += f' Running Tasks  : {self._runOrchestrator.running()}     \n'
            console += f' Queued Inputs  : {self._fuzzer_inputs.qsize()}     \n'
            console += f' Awaiting Fuzz  : {self._mutateOrchestrator.awaiting_fuzzing()}     \n'
            console += f' Task Q Size    : {self._limits["MIN_RUNNING_INPUTS"]} - {self._limits["MAX_RUNNING_INPUTS"]}\n'
            console += f' Fuzz Q Size    : {self._limits["MIN_QUEUED_INPUTS"]} - {self._limits["MAX_QUEUED_INPUTS"]}\n'
            console += f' Runner         : {"Stalled!" if self._runOrchestrator.stalled() else "OK"}          \n'
            console += f' Mutator        : {"Stalled!" if self._mutateOrchestrator.stalled() else "OK"}          \n'
            console += f' Max RSS        : {self._get_memory_usage_mb_()} MB (Limit {self._limits["MEMORY_LIMIT"]} MB)     \n'
            print(console)
            if self._checkOrchestrator.final_result()[0] is not None:
                print('*************')
                print('Fuzzing done!')
                print('*************')
                break
            time.sleep(1)

    def check_stall(self, delay):
        if delay < 3:
            return delay + 1
        if self._runOrchestrator.stalled():
            self._limits['MIN_RUNNING_INPUTS'] = min(int(self._limits['MIN_RUNNING_INPUTS'] * 1.2) + 1, 100)
            self._limits['MAX_RUNNING_INPUTS'] = min(int(self._limits['MAX_RUNNING_INPUTS'] * 1.2) + 1, 1000)
            if self._mutateOrchestrator.stalled():
                self._limits['MIN_QUEUED_INPUTS'] = min(int(self._limits['MIN_QUEUED_INPUTS'] * 1.2) + 1, 200)
                self._limits['MAX_QUEUED_INPUTS'] = min(int(self._limits['MAX_QUEUED_INPUTS'] * 1.2) + 1, 2000)
        return delay

    def run(self, binary):
        os.system('clear')
        self._stat_printer = Thread(target=self._print_stats_, name='stat-printer')
        self._stat_printer.start()
        delay = 0
        while True:
            delay = self.check_stall(delay)                  # Check if runner/mutator are running out of jobs
            self._runOrchestrator.run_new_inputs(binary)     # Start new jobs
            self._checkOrchestrator.check_finished_inputs()  # Check for finished jobs
            self._mutateOrchestrator.create_more_inputs()    # create new mutations
            if self._get_memory_usage_mb_() > self._limits['MEMORY_LIMIT']:
                self._mutateOrchestrator.cull_traces()           # cull traces of old mutations (limit memory)
            # time.sleep(0.1)
            if self._runOrchestrator.total_runs() > 20000:
                self._checkOrchestrator._final_code = 1234
                self._checkOrchestrator._final_input = 'hard exit'
            if self._checkOrchestrator.final_result()[0] is not None:
                self._runner.shutdown()
                break
        self._stat_printer.join()

    def __repr__(self):
        return f'Inputs waiting to run: {len(self._fuzzer_inputs.queue)} | Inputs running: {len(self._running_tasks.queue)}'


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
            if code != 0 and code != 134:  # abort doesn't count
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
        self._added_order = Queue()
        self._mutator = mutator
        self._distance = distance
        self._to_mutate = to_mutate
        self._fuzzer_inputs = fuzzer_inputs
        self._limits = limits
        self._strategy = dict() #sorry mickey i ceebs constructing it up in fuzzer, hope it doesnt matter.

    def _put_(self, _input, priority, previous, distance, strategy):
        self._fuzzer_inputs.put(QueueItem(_input, priority))
        self._added_order.put(_input)
        self._prev[_input] = previous
        self._distance[_input] = distance
        self._strategy[_input] = strategy

    def create_more_inputs(self):
        # creating inputs is memory and time expensive O(n^2), pause creating inputs if we have a lot ready to run
        if self.awaiting_fuzzing() > self._limits['MIN_QUEUED_INPUTS']:
            return
        while not self._to_mutate.empty() and self.awaiting_fuzzing() < self._limits['MAX_QUEUED_INPUTS']:
            _input = self._to_mutate.get()
            trace_info = self._seen[_input]
            for this_strategy in Strategy.STRATEGIES:
                for mutation in self._mutator.mutate(_input, strategy=this_strategy):
                    if mutation not in self._seen:
                        distance = self._distance[_input] + 1
                        priority = self._priority_function_(mutation, distance, trace_info)
                        self._put_(_input=mutation, 
                                   priority=priority,
                                   previous=_input,
                                   distance=distance,
                                   strategy=this_strategy)

    def cull_traces(self):
        limit = self._added_order.qsize() // 4
        while self._added_order.qsize() > limit:
            earliest = self._added_order.get()
            trace_info = self._seen.get(earliest, None)
            if trace_info is not None:
                trace_info.clear()

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
        
        if _input in self._prev and self._prev[_input] in self._strategy:
            strategy_discount = 10 if self._strategy[self._prev[_input]] == Strategy.ADD_DICTS else 1
        else: #deprioritise inputs that insert lots of shit
            strategy_discount = 1

        return -1/(distance+15)*(len(trace_info.jumps()) + unique_discovery)/strategy_discount

    def awaiting_fuzzing(self):
        return self._fuzzer_inputs.qsize()

    def stalled(self):
        return self.awaiting_fuzzing() == 0


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
