from fuzzylogic import mutator, executor

def fuzz(binary, input_file):
    print(f'binary: {binary}')
    print(f'input: {input_file}')
    with open(input_file, 'r') as f:
        content = f.read()
    print(f'Json: {mutator.isJson(content)}')
    print(f'Csv: {mutator.isCsv(content)}')
    print(f'Xml: {mutator.isXml(content)}')
    print(f'MultilineText: {mutator.isMultilineText(content)}')
    t = mutator.CsvMutator() #todo
    # print()
    runner = executor.runner()
    orchestrator = MutatorQueueOrchestrator(t)
    orchestrator.insert(PriorityShit(content, 1))
    while len(orchestrator):
        code = runner.run_process(binary, orchestrator.get()) # big todo (): if result code is not 0, save bad input to file.
        if code != 0: #segfault
            print(f'Exit code: {code}{" Segfault! :)" if code == -11 else " :("}')
            exit(0)
    

    print(" we finisehd without getting anything idk")

class MutatorQueueOrchestrator:
    def __init__(self, mutator): #type
        self.mutator = mutator
        self.q = [] #todo: import priority_queue

                    #big TODO: make a big hashmap mapping every input we've tried ----> its result
    
    def insert(self, priority_shit ):
        self.q.append(priority_shit)

    def get(self):
        to_mutate = self.q.pop(0)
        for mutation in self.mutator.mutate(to_mutate.data):
            self.q.append(PriorityShit(mutation, to_mutate.priority+1))
        return to_mutate.data
    
    def __len__(self):
        return len(self.q)
     


class PriorityShit:
    def __init__(self, data, priority):
        self.data = data
        self.priority = priority