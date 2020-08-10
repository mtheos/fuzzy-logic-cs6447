class TraceInfo:

    def __init__(self, jumps, arch):
        # self._jumps = jumps
        # TODO @Kapslock determine addr range by arch
        if arch == 'i386':  # trace is instructions so it's fine if the heap is in the range
            code_start = 0x08048000
            code_end = 0x09000000
        else:
            code_start = 0x00400000
            code_end = 0x00500000
        # self._jumps = sorted(set(jumps))  # sorted will make a list
        self._jumps = jumps
        self._edges = {}  # edges in the execution path
        # TODO @Kapslock should this be done before or after we turn the jumps into a sorted list
        for i in range(1, len(self._jumps)):
            if self._jumps[i] < code_start or self._jumps[i] > code_end or \
               self._jumps[i-1] < code_start or self._jumps[i-1] > code_end:
                continue
            if (self._jumps[i-1], self._jumps[i]) not in self._edges:
                self._edges[(self._jumps[i - 1], self._jumps[i])] = 1
            else:
                self._edges[(self._jumps[i - 1], self._jumps[i])] += 1
        self._jumps = sorted(set(jumps))  # sorted will make a list

    def jumps(self):
        return self._jumps

    def clear(self):
        self._jumps = []
        # self._edges = {}

    def __lt__(self, other):
        return self.priority_function() < other.priority_function()

    def __repr__(self):
        return f'Jumps: {self._jumps} idk lol'

    def __gt__(self, other):
        return self.priority_function() > other.priority_function()

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()  # equality by value

    def __hash__(self):
        return self.__repr__().__hash__()

    def priority_function(self):
        return len(self._jumps)
