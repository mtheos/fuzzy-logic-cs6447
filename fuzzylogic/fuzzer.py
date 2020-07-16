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
    print()
    runner = executor.runner()
    code = runner.run_process(binary, content)
    print(f'Exit code: {code}{" Segfault! :)" if code == -11 else " :("}')
