import json
import os
import socket
from io import StringIO
import itertools

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

    def all_resources(self):
        return list(itertools.chain(*[j['descriptors'] for i, j in self.processes.items()]))

    def get_resource(self, id):
        for i, proc in self.processes.items():
            for type in ['read', 'write']:
                for j, k in proc[type].items():
                    if id == j:
                        return k
        return None

    def get_process_by_pid(self, pid):
        return self.processes[pid]

    def read_file(self, id):
        return open(self.resource_path + "/" + id, 'rb').read()

class TracedData:
    def __init__(self):
        self.systems = []
        self.resources = {}

    def load(self, path):
        with open(os.path.join(path, 'data.json')) as file:
            self.systems.append(System(path, json.load(file)))

    def get_system(self, id):
        return self.systems[id]

    def create_graph(self):
        str = StringIO()
        dot_writer = DotWriter(str)
        dot_writer.begin()

        all = list(itertools.chain(*[i.all_resources() for i in self.systems]))
        network = [i for i in all if 'server' in i and i['server']]

        dot_writer.begin_subgraph('Network')
        for sock in network:
            dot_writer.write_node(self._format(sock), self._format(sock))
        dot_writer.end_subgraph()



        print(all)

        #dot_writer.begin_subgraph('Network')
        #for i in common:
        #    for id, resource in i.items():
        #        if resource['type'] == 'socket':
        #            dot_writer.write_node(id, self._format(resource))
        #dot_writer.end_subgraph()

        mymap = {}

        def _hash(addr):
            return "%s:%s" % (addr['address'], addr['port'])

        for system in self.systems:
            for pid, process in system.processes.items():
                for descriptor in process['descriptors']:
                    if 'family' in descriptor and descriptor['family'] in [socket.AF_INET, socket.AF_INET6]:
                        if '0.0.0.0' not in descriptor['local']['address']:
                            mymap[_hash(descriptor['local'])] = pid

        i = 0
        for system in self.systems:
            i += 1
            dot_writer.begin_subgraph("node #%d" % i)
            for pid, process in system.processes.items():
                dot_writer.write_node(pid, process['executable'])

                if process['parent'] > 0:
                    dot_writer.write_edge(process['parent'], pid)

                for name in process['descriptors']:
                    dot_writer.write_node(self._format(name), self._format(name))
                    self.resources[self._format(name)] = name

                    if 'server' in name and name['server']:
                        dot_writer.write_edge(pid, self._format(name))

                    if 'read_content' in name:
                        dot_writer.write_edge(self._format(name), pid)

                    if 'write_content' in name:
                        dot_writer.write_edge(pid, self._format(name))

            dot_writer.end_subgraph()

        for system in self.systems:
            for pid, process in system.processes.items():
                for name in process['descriptors']:
                    if name['type'] == 'socket' and name['family'] in [socket.AF_INET, socket.AF_INET6]:
                        if '0.0.0.0' in name['local']['address'] and name['remote']:
                            dot_writer.write_edge(_hash(name['local']), mymap[_hash(name['remote'])])

        dot_writer.end()

        with open("/tmp/a.dot", "w") as f:
            f.write(str.getvalue())

        import os
        os.system("sh -c 'dot -Txdot /tmp/a.dot > /tmp/a.xdot'")

        parser = XDotParser(open("/tmp/a.xdot").read().encode('utf-8'), self)
        return parser.parse()

    def _format(self, fd):
        if fd['type'] == 'socket':
                if fd['family'] in [socket.AF_INET, socket.AF_INET6] and fd['local']: # TODO: quickfix
                    if fd['remote'] is None:
                        return "%s:%d" % (fd['local']['address'], fd['local']['port'])

                    return "%s:%d\\n<->\\n%s:%d" % (
                        fd['local']['address'], fd['local']['port'],
                        fd['remote']['address'], fd['remote']['port']
                    )
                return "socket: %d" % fd['family']

        if fd['type'] == 'file':
            return fd['path']

        if fd['type'] == 'pipe':
            return 'pipe' # TODO: add identification of pipe
