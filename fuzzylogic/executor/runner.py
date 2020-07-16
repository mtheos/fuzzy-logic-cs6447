from subprocess import Popen, PIPE


class runner:
    def __init__(self):
        pass

    def run_process(self, binary, _input):
        p = Popen(binary, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(_input.encode())
        code = p.wait()
        return code
