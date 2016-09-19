class DotWriter:
    def __init__(self, out):
        self.out = out

    def begin(self):
        self.out.write("digraph G {\n")

    def end(self):
        self.out.write("}\n")

    def write_node(self, id, title):
        self.out.write('\t"%s" [label="%s"];\n' % (self._escape(id), self._escape(title)))

    def write_edge(self, src, dst):
        self.out.write('\t"%s" -> "%s";\n' % (self._escape(src), self._escape(dst)))

    def _escape(self, s):
        return str(s).replace('"', '\\"')
