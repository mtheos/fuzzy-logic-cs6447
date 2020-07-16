class JsonMutator :
    def __init__(self):
        self.seed = 0

    #return a generator (i.e. list)
    def mutate(self, json_object):
        self.seed += 1
        return json_object

        #todo: call int .... mutator aran and mikey