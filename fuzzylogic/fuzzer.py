from fuzzylogic import mutator, executor
from .fuzzOrchestrator import FuzzOrchestrator


def fuzz(binary, input_file):
    print(f'binary: {binary}')
    print(f'input: {input_file}')
    with open(input_file, 'r') as f:
        content = f.read()
    mutator_instance = _select_mutator_(content)
    runner = executor.ThreadedRunner()
    orchestrator = FuzzOrchestrator(mutator_instance, runner)
    orchestrator.put(content, priority=-1e9)
    orchestrator.put(mutator_instance.empty(), priority=-1e9)
    orchestrator.run(binary)
    code, _input, runs = orchestrator.final_result()
    console = f'\n\n {"*" * 40}\n'
    console += f' We did it Reddit! (Nice work fam ^_^)\n'
    console += f' {runs} inputs tried\n'
    console += f' Exit code: {code} => {runner.parse_code(code)}\n'
    console += f' {"*" * 40}\n'
    print(console)
    with open('bad.txt', 'w') as f:
        f.write(_input + '\n')


def _select_mutator_(content):
    content_type = mutator.detect(content)
    if content_type == mutator.RET_FAIL:
        raise Exception('Failed to detect input type')
    if content_type == mutator.RET_JSON:
        print('Input Type: JSON')
        mutator_instance = mutator.JsonMutator()
    elif content_type == mutator.RET_CSV:
        print('Input Type: CSV')
        mutator_instance = mutator.CsvMutator()
    elif content_type == mutator.RET_XML:
        print('Input Type: XML')
        mutator_instance = mutator.XmlMutator()
    elif content_type == mutator.RET_MULTILINE_TEXT:
        print('Input Type: Plain Text')
        mutator_instance = None
    else:
        raise Exception(f'Failed to select mutator for input type.\nContent Type{content_type}')
    return mutator_instance
