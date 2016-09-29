import json
import os
from io import StringIO

from DotWriter import DotWriter
from dot.parser import XDotParser


class Process:
    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        return self.data[item]


class System:
    def __init__(self, resource_path, data):
        self.processes = {}
        self.resource_path = resource_path

        for id, process in data.items():
            self.processes[int(id)] = Process(process)

    def get_process_by_pid(self, pid):
        return self.processes[pid]

    def read_file(self, id):
        return open(self.resource_path + "/" + id, 'rb').read()

class TracedData:
    def __init__(self):
        self.systems = []

    def load(self, path):
        with open(os.path.join(path, 'data.json')) as file:
            self.systems.append(System(path, json.load(file)))

    def get_system(self, id):
        return self.systems[id]

    def create_graph(self):
        str = StringIO()
        dot_writer = DotWriter(str)
        dot_writer.begin()

        i = 0
        for system in self.systems:
            i += 1
            dot_writer.begin_subgraph("node #%d" % i)
            for pid, process in system.processes.items():
                dot_writer.write_node(pid, process['executable'])

                if process['parent'] > 0:
                    dot_writer.write_edge(process['parent'], pid)

                def format(fd):
                    if 'file' in fd:
                        return fd['file']

                    if 'src' in fd:
                        return "%s:%d\\n<->\\n%s:%d" % (
                            fd['src']['address'], fd['src']['port'],
                            fd['dst']['address'], fd['dst']['port']
                        )

                    if fd['type'] == 'pipe':
                        return 'pipe:[%s]' % fd['inode']

                    return fd

                for id, name in process['read'].items():
                    dot_writer.write_node(id, format(name))
                    dot_writer.write_edge(id, pid)

                for id, name in process['write'].items():
                    dot_writer.write_node(id, format(name))
                    dot_writer.write_edge(pid, id)

            dot_writer.end_subgraph()
        dot_writer.end()

        with open("/tmp/a.dot", "w") as f:
            f.write(str.getvalue())

        import os
        os.system("sh -c 'dot -Txdot /tmp/a.dot > /tmp/a.xdot'")

        parser = XDotParser(open("/tmp/a.xdot").read().encode('utf-8'), self)
        return parser.parse()
