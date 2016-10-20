class Bag:
    def __init__(self):
        self.id = 0
        self.data = {}

    def write(self, data):
        self.data[self.id] = data
        self.id += 1
        return self.id - 1

    def get(self, id):
        return self.data[id]

class DotWriter:
    def __init__(self, out):
        self.out = out
        self.subgraph_id = 0
        self.bag = Bag()

    def begin(self):
        self.out.write("digraph G {\n")

    def end(self):
        self.out.write("}\n")

    def begin_subgraph(self, title):
        self.out.write("subgraph cluster_%d {\n" % self.subgraph_id)
        self.out.write("label = \"%s\";" % self._escape(title))
        self.subgraph_id += 1

    def end_subgraph(self):
        self.out.write("}\n")

    def write_node(self, id, title):
        self.out.write('\t"%s" [label="%s"];\n' % (self._escape(id), self._escape(title)))

    def write_edge(self, src, dst, data=None, **kwargs):
        if data is not None:
            kwargs['data_id'] = self.bag.write(data)

        args = ", ".join(["%s=\"%s\"" % (i, self._escape(j)) for i, j in kwargs.items()])
        self.out.write('\t"%s" -> "%s" [%s];\n' % (self._escape(src), self._escape(dst), args))

    def write_biedge(self, node1, node2, **kwargs):
        kwargs['dir'] = 'none'
        self.write_edge(node1, node2, **kwargs)

    def _escape(self, s):
        return str(s).replace('"', '\\"')

