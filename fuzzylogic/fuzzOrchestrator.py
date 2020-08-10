import os
import time
import psutil
import resource
from queue import PriorityQueue, Queue
from threading import Thread
from .strategy import Strategy
class FuzzOrchestrator:
    def __init__(self, mutator, runner):
        self._seen = dict()
        self._prev = dict()
        self._dist = dict()
        self._runner = runner
        self._mutator = mutator
        self._skip_stall_check = True  # skip early stall checks to let things settle
        self._start_time = None
        self._to_mutate = Queue()
        self._stat_printer = None
        self._running_tasks = Queue()
        self._fuzzer_inputs = PriorityQueue()
        # larger limits run faster, but fill up the runner with earlier "generations" of inputs
        self._limits = {
            'MAX_RUNNING_INPUTS': runner.num_workers() * 2,
            'MIN_QUEUED_INPUTS': runner.num_workers() * 2,
            'MAX_QUEUED_INPUTS': runner.num_workers() * 3,
            # We use as much memory as we need but leave a small buffer so we don't get killed
            'MEMORY_BUFFER': 400,
        }
        self._runOrchestrator = RunOrchestrator(runner, self._fuzzer_inputs, self._running_tasks, self._limits)
        self._checkOrchestrator = CheckOrchestrator(runner, self._fuzzer_inputs, self._running_tasks, self._to_mutate, self._seen, self._limits)
        self._mutateOrchestrator = MutateOrchestrator(mutator, self._fuzzer_inputs, self._to_mutate, self._seen, self._dist, self._prev,
                                                      self._limits)

    def run(self, binary):
        self._start_time = time.time()
        self._stat_printer = Thread(target=self._print_stats_, name='stat-printer', args=(binary,))
        self._stat_printer.start()
        try:
            self._run_(binary)
            self._runner.shutdown(True)
            self._stat_printer.join()
        except KeyboardInterrupt:
            self._checkOrchestrator._final_code = 6447
            self._checkOrchestrator._final_input = 'User exit'
            self._runner.shutdown(True)
            self._stat_printer.join()
        # except Exception as e:
        #     self._checkOrchestrator._final_code = 6448
        #     self._checkOrchestrator._final_input = e
        #     self._runner.shutdown(True)
        #     self._stat_printer.join()
        #     raise

    def _run_(self, binary):
        while True:
            self.check_stall()  # Check if runner/mutator are running out of jobs
            self._runOrchestrator.run_new_inputs(binary)  # Start new jobs
            self._checkOrchestrator.check_finished_inputs()  # Check for finished jobs
            self._mutateOrchestrator.create_more_inputs()  # create new mutations
            if self._get_free_memory_mb_() < self._limits['MEMORY_BUFFER']:
                self._mutateOrchestrator.cull_traces()  # cull traces of old mutations (limit memory)
            # if self._checkOrchestrator.completed_runs() > 5000:
            #     self._checkOrchestrator._final_code = 6847
            #     self._checkOrchestrator._final_input = 'Debug exit'
            if self._checkOrchestrator.final_result()[0] is not None:
                break

    def put(self, _input, priority, previous=None, distance=0):
        self._fuzzer_inputs.put(QueueItem(_input, priority))
        self._prev[_input] = previous
        self._dist[_input] = distance

    def final_result(self):
        return (*self._checkOrchestrator.final_result(), self._checkOrchestrator.completed_runs())

    def _print_stats_(self, binary):
        print('\n Fuzzy-Logic-6447 - "Our logic is fuzzy but our minds are sharp"\n')
        print('\033[s')  # save cursor position
        while True:
            m, s = divmod(int(time.time() - self._start_time), 60)
            console = f'\033[u'
            console += f' Binary         : {binary} ({self._runner.get_arch()})\n'
            console += f' Elapsed        : {m}:{str(s).zfill(2)}\n'
            console += f' Total attempts : {self._checkOrchestrator.completed_runs()}\n'
            console += f' Worker Count   : {self._runner.num_workers()}\n'
            console += f' Running Tasks  : {self._runOrchestrator.running()}     \n'
            console += f' Queued Inputs  : {self._fuzzer_inputs.qsize()}     \n'
            console += f' Awaiting Fuzz  : {self._mutateOrchestrator.awaiting_fuzzing()}     \n'
            console += f' Task Q Size    : 0 - {self._limits["MAX_RUNNING_INPUTS"]}\n'
            console += f' Fuzz Q Size    : {self._limits["MIN_QUEUED_INPUTS"]} - {self._limits["MAX_QUEUED_INPUTS"]}\n'
            console += f' Runner         : {"Stalled!" if self._runOrchestrator.stalled() else "OK"}          \n'
            console += f' Mutator        : {"Stalled!" if self._mutateOrchestrator.stalled() else "OK"}          \n'
            console += f' Max RSS        : {self._get_memory_rss_mb_()} MB (Free {self._get_free_memory_mb_()} MB)     \n'
            console += f' Ctrl+C to exit\n'
            print(console)
            if self._checkOrchestrator.final_result()[0] is not None:
                print('\n\n *************')
                if self._checkOrchestrator.final_result()[0] == 6447:
                    print(' User exit')
                else:
                    print(' Fuzzing done!')
                print(' *************')
                break
            time.sleep(0.5)

    def check_stall(self):
        if self._skip_stall_check:
            if ((time.time() - self._start_time) % 60) > 2:
                self._skip_stall_check = False
            return
        # tighter limits are better, in any case avoid the blow out to infinity issue
        if self._runOrchestrator.stalled():
            self._runOrchestrator.clear_stalled()
            self._limits['MAX_RUNNING_INPUTS'] = min(int(self._limits['MAX_RUNNING_INPUTS'] * 1.2) + 1, self._runner.num_workers() * 50)
            self._limits['MIN_QUEUED_INPUTS'] = self._limits['MAX_RUNNING_INPUTS']
            self._limits['MAX_QUEUED_INPUTS'] = self._limits['MIN_QUEUED_INPUTS'] + self._runner.num_workers()
        if self._mutateOrchestrator.stalled():
            self._limits['MIN_QUEUED_INPUTS'] = min(int(self._limits['MIN_QUEUED_INPUTS'] * 1.2) + 1, self._runner.num_workers() * 10)
            self._limits['MAX_QUEUED_INPUTS'] = min(int(self._limits['MAX_QUEUED_INPUTS'] * 1.2) + 1, self._runner.num_workers() * 11)

    @staticmethod
    def _get_memory_rss_mb_():
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000)

    @staticmethod
    def _get_free_memory_mb_():
        return int(psutil.virtual_memory().available / 1000000)

    def __repr__(self):
        return f'Inputs waiting to run: {len(self._fuzzer_inputs.queue)} | Inputs running: {len(self._running_tasks.queue)}'


class RunOrchestrator:
    def __init__(self, runner, fuzzer_inputs, running_tasks, limits):
        self._runner = runner
        self._fuzzer_inputs = fuzzer_inputs
        self._running_tasks = running_tasks
        self._limits = limits

    def run_new_inputs(self, binary):
        # too many binaries is inefficient as new cases could have better priority
        while self.has_inputs() and self.running() < self._limits['MAX_RUNNING_INPUTS']:
            _input = self._fuzzer_inputs.get().data
            self._running_tasks.put(self._runner.run_process(binary, _input))

    def has_inputs(self):
        return not self._fuzzer_inputs.empty()

    def running(self):
        return self._running_tasks.qsize()

    def stalled(self):
        return self._runner.stalled()

    def clear_stalled(self):
        self._runner.clear_stalled()


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
        self._completed = 0

    def final_result(self):
        return self._final_code, self._final_input

    def completed_runs(self):
        return self._completed

    def check_finished_inputs(self):
        loop_check = None
        while not self._running_tasks.empty():
            task_id = self._running_tasks.get()
            if not self._runner.is_done(task_id):  # If the task is not complete put it back in the queue
                self._running_tasks.put(task_id)
                if loop_check is not None and loop_check == task_id:
                    break  # looped back to first thing we put back in
                if loop_check is None:
                    loop_check = task_id  # first id is the loop check
                continue
            code, _input, trace_info = self._runner.get_result(task_id)
            self._completed += 1
            if code == 139:  # We only look at segfaults
                self._final_input = _input
                self._final_code = code
            self._seen[_input] = trace_info
            self._to_mutate.put(_input)

    def has_inputs(self):
        return not self._fuzzer_inputs.empty()

    def running(self):
        return self._running_tasks.qsize()


class MutateOrchestrator:
    def __init__(self, mutator, fuzzer_inputs, to_mutate, seen, dist, prev, limits):
        self._seen = seen
        self._prev = prev
        self._dist = dist
        self._limits = limits
        self._strategy = dict()
        self._mutator = mutator
        self._to_mutate = to_mutate
        self._added_order = Queue()
        self._fuzzer_inputs = fuzzer_inputs

    def _put_(self, _input, priority, previous, distance, strategy):
        self._added_order.put(_input)
        self._prev[_input] = previous
        self._dist[_input] = distance
        self._strategy[_input] = strategy
        self._fuzzer_inputs.put(QueueItem(_input, priority))

    def create_more_inputs(self):
        # creating inputs is memory and time expensive, pause creating inputs if we have a lot ready to run
        if self.awaiting_fuzzing() > 100000: #self._limits['MIN_QUEUED_INPUTS']:
            return
        while not self._to_mutate.empty() and self.awaiting_fuzzing() < self._limits['MAX_QUEUED_INPUTS']:
            _input = self._to_mutate.get()
            trace_info = self._seen[_input]
            things_so_far = len(self._seen.keys()) + self._fuzzer_inputs._qsize()
            #big TODO: this is the switch from the 'early' strategies to the 'late' strategies. 
            #late strategies are more random. later we will detect how long the program has run and do the
            #late strategies later.



            #improtant not: make this small when testing (for instant results), but higher in submission for 
            #better coverage
            EARLY_LATE_SWITCH = 100

            if things_so_far < EARLY_LATE_SWITCH:
                strats = Strategy.EARLY_STRATEGIES
            else:
                strats = Strategy.LATE_STRATEGIES

            for this_strategy in strats:
                for mutation in self._mutator.mutate(_input, strategy=this_strategy):
                    if mutation not in self._seen:
                        distance = self._dist[_input] + 1
                        priority = self._priority_function_(mutation, distance, trace_info)
                        self._put_(_input=mutation, priority=priority, previous=_input, distance=distance, strategy=this_strategy)

    # Need to limit memory usage to something reasonable...
    # Clear our the trace info for the earliest inputs (hopefully these have been fuzzed by now)
    def cull_traces(self):
        limit = self._added_order.qsize() // 4 * 3
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
        else:  # deprioritise inputs that insert lots of shit
            strategy_discount = 1

        return -1 / (distance + 20) * (len(trace_info.jumps()) + unique_discovery) / strategy_discount

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
