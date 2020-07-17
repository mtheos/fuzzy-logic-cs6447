from fuzzylogic import mutator, executor


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
        mutator_instance = None
    else:
        mutator_instance = None
    print(f'mutator: {mutator_instance}')
    runner = executor.Runner()
    orchestrator = MutatorQueueOrchestrator(mutator_instance)
    orchestrator.insert(PriorityShit(content, 1))
    while len(orchestrator):
        _input = orchestrator.get()
        code = runner.run_process(binary, _input)  # big todo (mikey): if result code is not 0, save bad input to file.
        if code != 0:
            print(f'Exit code: {code} => {runner.parse_code(code)}')
            print('\n' + '*' * 20)
            print(f"\n\nI'm just not writing output right now... Uncomment the lines below this to save to file :)\n\n")
            print('*' * 20)
            # with open('bad.txt', 'w') as f:
            #     f.write(_input + '\n')
            break
    else:
        print("We dun fucked up... :'(")


class MutatorQueueOrchestrator:
    def __init__(self, mutator_instance):
        self._mutator = mutator_instance
        self._q = []  # todo: import priority_queue
        #  big TODO: make a big hashmap mapping every input we've tried ----> its result
        #  Andrew

    def insert(self, priority_shit):
        self._q.append(priority_shit)

    def get(self):
        to_mutate = self._q.pop(0)
        for mutation in self._mutator.mutate(to_mutate.data):
            self._q.append(PriorityShit(mutation, to_mutate.priority + 1))
        return to_mutate.data

    def __len__(self):
        return len(self._q)

    def __repr__(self):
        return f'Items: {len(self._q)}'


class PriorityShit:
    def __init__(self, data, priority):
        self.data = data
        self.priority = priority

    def __repr__(self):
        return f'({self.priority}) "{self.data}"'
