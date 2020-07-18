from fuzzylogic import mutator, executor
from queue import PriorityQueue
import json
import collections


def fuzz(binary, input_file):
    print(f'binary: {binary}')
    print(f'input: {input_file}')
    with open(input_file, 'r') as f:
        content = f.read()
    if mutator.isJson(content):
        mutator_instance = mutator.JsonMutator()
    elif mutator.isXml(content):
        mutator_instance = None
    elif mutator.isCsv(content):
        mutator_instance = mutator.CsvMutator()
    elif mutator.isMultilineText(content):
        mutator_instance = mutator.CsvMutator()  # NOTE: this is TEMPORARY for ez debugging
    else:
        mutator_instance = mutator.CsvMutator()  # NOTE: this is TEMPORARY for ez debugging

    print(f'mutator: {mutator_instance}')
    runner = executor.Runner()
    orchestrator = MutatorQueueOrchestrator(mutator_instance)
    orchestrator.insert(PriorityShit(content, 0))
    orchestrator.insert(PriorityShit(mutator_instance.empty(), 0))
    while len(orchestrator):
        _input = orchestrator.get()
        # code = runner.run_process(binary, _input)
        code = runner.run_process(binary, _input, fake=True)  # always return 0
        if code != 0:
            print(f'Exit code: {code} => {runner.parse_code(code)}')
            print('\n' + '*' * 20)
            print(f"I'm just not writing output right now...\nUncomment the lines below this to save to file :)")
            print('*' * 20)
            # with open('bad.txt', 'w') as f:
            #     f.write(_input + '\n')
            break
    else:
        print("We dun fucked up... :'(")


class MutatorQueueOrchestrator:
    def __init__(self, mutator_instance):
        self._mutator = mutator_instance
        self._q = PriorityQueue() 
        self.seen = dict()

    def insert(self, priority_shit):
        self._q.put(priority_shit)

    def get(self):
        to_mutate = self._q.get()
        for mutation in self._mutator.mutate(to_mutate.data):
            if mutation not in self.seen:
                self._q.put(PriorityShit(mutation, to_mutate.priority + 1))
                self.seen[mutation] = 1
        return to_mutate.data

    def __len__(self):
        return self._q.qsize()

    def __repr__(self):
        return f'Items: {len(self._q.queue)}'

    def empty(self):
        return self._q.empty()


# todo(Andrew): rename this to queue_item, and make another class for the
# actual priority
class PriorityShit:
    def __init__(self, data, priority):
        self.data = data
        self.priority = priority

    # from what I can see, PriorityQueue only uses < comparisons
    def __lt__(self, other):
        return self.priority < other.priority

    def __repr__(self):
        return f'({self.priority}) "{self.data}"'
    
    def __gt__(self, data2):
        return self.priority_function(self.priority) > self.priority_function(data2.priority)

    def __eq__(self, x):
        return self.__repr__() == x.__repr__()  # equality by value

    def __hash__(self):
        return self.__repr__().__hash__()

    def priority_function(self, priority):
        return priority