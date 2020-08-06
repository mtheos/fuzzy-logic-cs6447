class TraceInfo:
    def __init__(self, jumps):
        # self._jumps = jumps
        self._jumps = sorted(set(jumps))  # sorted will make a list
        # self._edges = {}  # edges in the execution path
        # for i in range(1, len(self._jumps)):
        #     if (self._jumps[i-1], self._jumps[i]) not in self._edges:
        #         self._edges[(self._jumps[i - 1], self._jumps[i])] = 1
        #     else:
        #         self._edges[(self._jumps[i - 1], self._jumps[i])] += 1

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
