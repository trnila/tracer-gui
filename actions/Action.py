class Action:
    def __init__(self, system):
        self.system = system
        self.edges = []
        self.res = []

    def generate(self, dot_writer):
        pass

    def gui(self, window, graph):
        pass

    def apply_filter(self, query):
        raise NotImplemented
