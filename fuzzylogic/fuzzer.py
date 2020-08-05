from fuzzylogic import mutator, executor
from queue import PriorityQueue

NO_STRATEGY = 'no strategy / random strategy for now'
MAKE_ZERO = 'make_zero'

def fuzz(binary, input_file):
    print(f'binary: {binary}')
    print(f'input: {input_file}')
    with open(input_file, 'r') as f:
        content = f.read()
    content_type = mutator.detect(content)
    if content_type == mutator.RET_FAIL:
        raise Exception('Failed to detect input type')
    if content_type == mutator.RET_JSON:
        mutator_instance = mutator.JsonMutator()
    elif content_type == mutator.RET_CSV:
        mutator_instance = mutator.CsvMutator()
    elif content_type == mutator.RET_XML:
        mutator_instance = None
    elif content_type == mutator.RET_MULTILINE_TEXT:
        mutator_instance = mutator.CsvMutator()
    else:
        mutator_instance = None

    runner = executor.Runner()
    orchestrator = MutatorQueueOrchestrator(mutator_instance)
    distance = dict()
    prev = dict()
    orchestrator._q.put(QueueItem(content, -1e9))
    distance[content] = 0
    orchestrator._q.put(QueueItem(mutator_instance.empty(), -1e9))
    distance[mutator_instance.empty()] = 0
    runs = 0

    #return negative weighting. (lower is higher priority)
    def priority_function(the_input, priority_info):
        d = distance[the_input]
        

        # calculate the unique discovery of a block bonus
        if _input not in prev:
            prev_jumps = {}
        else:
            prev_jumps = set(orchestrator.seen[prev[_input]].jumps)
        unique_discovery = 0
        for j in priority_info.jumps:
            if j not in prev_jumps:
                unique_discovery = 15000
                break
        return  -1/(d+15)*(len(priority_info.jumps)+ unique_discovery)

    while len(orchestrator):
        runs += 1
        # if runs % 100 == 0:
        #     print("runs = ", runs)
        _input = orchestrator.get()
        priority_info = runner.run_process(binary, _input)
        code = priority_info.return_code
        orchestrator.seen[_input] = priority_info

        #later, we will actuallly use a strategy. right now strategies are shit
        for mutation in orchestrator._mutator.mutate(_input, NO_STRATEGY):
            if mutation not in orchestrator.seen:
                prev[mutation] = _input
                distance[mutation] = distance[_input] + 1
                orchestrator._q.put(QueueItem(mutation, priority_function(mutation, priority_info)))

        if code != 0:
            print('*' * 20)
            print('We did it Reddit! (Nice work fam ^_^)')
            print(f'{runs} inputs tried')
            print(f'Exit code: {code} => {runner.parse_code(code)}')
            print('*' * 20)
            with open('bad.txt', 'w') as f:
                f.write(_input + '\n')
            break
    else:
        print("We dun fucked up... :'(")


class MutatorQueueOrchestrator:
    def __init__(self, mutator_instance):
        self._mutator = mutator_instance
        self._q = PriorityQueue()
        self.seen = dict()

    def get(self):
        to_mutate = self._q.get()
        return to_mutate.data

    def __len__(self):
        return self._q.qsize()

    def __repr__(self):
        return f'Items: {len(self._q.queue)}'

    def empty(self):
        return self._q.empty()


# todo(Andrew): rename this to queue_item, and make another class for the
# actual priority
class QueueItem:
    def __init__(self, data, priority):
        self.data = data
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority
    
    def __gt__(self, data2):
        return self.priority > data2.priority

    def __eq__(self, x):
        return self.priority == x.priority  # equality by value

    def __hash__(self):
        return self.__repr__().__hash__()

    # from what I can see, PriorityQueue only uses < comparisons