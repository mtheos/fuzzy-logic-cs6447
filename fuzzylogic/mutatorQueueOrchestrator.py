from queue import PriorityQueue
from queue import Queue


class MutatorQueueOrchestrator:
    _min_running_ = 50
    _max_running_ = 100

    def __init__(self, mutator, runner):
        self._mutator = mutator
        self._runner = runner
        self._fuzzer_inputs = PriorityQueue()
        self._running_tasks = Queue()
        self._seen = dict()
        self._distance = dict()
        self._prev = dict()
        self._runs = 0
        self._final_input = None
        self._final_code = None

    def final_result(self):
        return self._final_code, self._final_input, self._runs

    def put(self, _input, priority, previous=None, distance=0):
        self._fuzzer_inputs.put(QueueItem(_input, priority))
        self._prev[_input] = previous
        self._distance[_input] = distance

    def get(self):
        to_mutate = self._fuzzer_inputs.get()
        return to_mutate.data

    def run(self, binary):
        while True:
            self._add_new_tasks_(binary)
            self._create_more_tasks_()
            if self._final_code:
                self._runner.shutdown()
                break

    def _add_new_tasks_(self, binary):
        # too many binaries is inefficient as new cases could have better priority
        while self.has_inputs() and self.running() < self._max_running_:
            self._runs += 1
            _input = self.get()
            self._running_tasks.put(self._runner.run_process(binary, _input))

    def _create_more_tasks_(self):
        loop_check = None
        while not self._running_tasks.empty() and (self.running() > self._min_running_ or not self.has_inputs()):
            task_id = self._running_tasks.get()
            if not self._runner.is_done(task_id):  # If the task is not complete put it back in the queue
                self._running_tasks.put(task_id)
                if loop_check is not None and loop_check == task_id:
                    break  # looped back to first thing we put back in
                if loop_check is None:
                    loop_check = task_id  # first id is the loop check
                continue
            code, _input, trace_info = self._runner.get_result(task_id)
            # print(f'queued: {self._fuzzer_inputs.qsize()}, Running: {self.running()}')
            if code != 0:
                self._final_input = _input
                self._final_code = code
                return
            self._seen[_input] = trace_info
            for mutation in self._mutator.mutate(_input):
                if mutation not in self._seen:
                    # self._prev[mutation] = _input
                    distance = self._distance[_input] + 1
                    priority = self._priority_function_(mutation, distance, trace_info)
                    self.put(_input=mutation, priority=priority, previous=_input, distance=distance)

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

    def has_inputs(self):
        return not self._fuzzer_inputs.empty()

    def running(self):
        return self._running_tasks.qsize()

    def __repr__(self):
        return f'Inputs waiting to run: {len(self._fuzzer_inputs.queue)} | Inputs running: {len(self._running_tasks.queue)}'


# todo(Andrew): rename this to queue_item, and make another class for the
# actual priority
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
