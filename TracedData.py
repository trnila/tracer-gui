import itertools
import json
import os
import socket
from io import StringIO

import maps
from DotWriter import DotWriter
from dot.parser import XDotParser


def _id(fd, system):
    if fd['type'] == 'file':
        return "%s_%s" % (system.resource_path, fd['path'])

    if fd['type'] == 'pipe':
        return "%s_%s" % (id(system), fd['pipe_id'])

    if fd['type'] == 'socket' and fd['domain'] in [socket.AF_INET, socket.AF_INET6]:
        try:
            parts = sorted([
                fd['local']['address'],
                str(fd['local']['port']),
                fd['remote']['address'],
                str(fd['remote']['port']),
            ])

            return "socket_%s" % (":".join(parts))
        except:
            pass

    return _format(fd)


def _format(fd):
    if fd['type'] == 'socket':
        if fd['domain'] == socket.AF_UNIX:
            return "unix:%s" % (fd['remote'])

        if fd['domain'] in [socket.AF_INET, socket.AF_INET6] and fd['local']:  # TODO: quickfix
            if fd['remote'] is None:
                return "%s:%d" % (fd['local']['address'], fd['local']['port'])

            return "%s:%d\\n<->\\n%s:%d" % (
                fd['local']['address'], fd['local']['port'],
                fd['remote']['address'], fd['remote']['port']
            )
        return "socket: %s #%s" % (fd['domain'], fd['socket_id'])

    if fd['type'] == 'file':
        return fd['path']

    if fd['type'] == 'pipe':
        return 'pipe: %d' % fd['pipe_id']


class Action:
    def __init__(self, system):
        self.system = system

    def generate(self, dot_writer):
        pass


class ProcessCreated(Action):
    def __init__(self, system, process, parent=None):
        super().__init__(system)
        self.process = process
        self.parent = parent

    def generate(self, dot_writer):
        dot_writer.write_node(self.process['pid'], self.process['executable'])

        if self.parent:
            dot_writer.write_edge(self.parent['pid'], self.process['pid'])

class Des(Action):
    def __init__(self, descriptor):
        super().__init__(None)
        self.descriptor = descriptor

    def generate(self, dot_writer):
        raise NotImplemented()


class ReadDes(Des):
    def generate(self, dot_writer):
        dot_writer.write_edge(
            _id(self.descriptor, self.descriptor.process.system),
            self.descriptor.process['pid'],
            data=self.descriptor['read_content'],
        )


class WriteDes(Des):
    def generate(self, dot_writer):
        dot_writer.write_edge(
            self.descriptor.process['pid'],
            _id(self.descriptor, self.descriptor.process.system),
            data=self.descriptor['write_content'],
        )

class Mmap(Des):
    def generate(self, dot_writer):
        dot_writer.write_biedge(
            self.descriptor.process['pid'],
            _id(self.descriptor, self.descriptor.process.system),
            data=self.descriptor
        )

class Descriptor:
    def __init__(self, process, data):
        self.data = data
        self.process = process

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

class Process:
    def __init__(self, system, data):
        self.system = system
        self.data = data

        self.data['descriptors'] = [Descriptor(self, i) for i in self.data['descriptors']]

    def __getitem__(self, item):
        return self.data[item]


class System:
    def __init__(self, resource_path, data):
        self.processes = {}
        self.resource_path = resource_path

        for id, process in data.items():
            self.processes[int(id)] = Process(self, process)

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

    def create_graph(self, filter=None):
        str = StringIO()
        dot_writer = DotWriter(str)
        dot_writer.begin()

        all = list(itertools.chain(*[i.all_resources() for i in self.systems]))
        network = [i for i in all if 'server' in i and i['server']]
        network = [i for i in all if i['type'] == 'socket' and 'domain' in i and i['domain'] in [socket.AF_INET, socket.AF_INET6]]

        dot_writer.begin_subgraph('Network')
        for sock in network:
            dot_writer.write_node(self._id(sock, 1), self._format(sock))
        dot_writer.end_subgraph()

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
                parent = system.get_process_by_pid(process['parent']) if process['parent'] > 0 else None
                ProcessCreated(system, process, parent).generate(dot_writer)

                # kills
                for kill in process['kills']:
                    dot_writer.write_edge(pid, kill['pid'], label=maps.signals[kill['signal']])

                for name in process['descriptors']:
                    if filter and filter in self._format(name):
                        continue

                    #if name['type'] == 'socket' and 'server' in name and not name['server'] and len(self.systems) > 1:
                     #   continue

                    dot_writer.write_node(self._id(name, system), self._format(name))
                    self.resources[self._id(name, system)] = name

                    #if 'server' in name and name['server']:
                    #    dot_writer.write_edge(pid, self._id(name, system))

                    if 'read_content' in name:
                        ReadDes(name).generate(dot_writer)

                    if 'write_content' in name:
                        WriteDes(name).generate(dot_writer)

                    if 'mmap' in name and len(name['mmap']):
                        Mmap(name).generate(dot_writer)

            dot_writer.end_subgraph()

        sys = 0
        for system in self.systems:
            for pid, process in system.processes.items():
                for name in process['descriptors']:
                    if name['type'] == 'socket' and name['domain'] in [socket.AF_INET, socket.AF_INET6]:
                        if '0.0.0.0' in name['local']['address'] and name['remote']:
                            try:
                                dot_writer.write_edge(_hash(name['local']), mymap[_hash(name['remote'])],
                                                      file=name['write_content'], system=sys)
                                dot_writer.write_edge(mymap[_hash(name['remote'])], _hash(name['local']),
                                                      file=name['read_content'], system=sys)
                            except:
                                print("err")

            sys += 1

        dot_writer.end()

        with open("/tmp/a.dot", "w") as f:
            f.write(str.getvalue())

        import os
        os.system("sh -c 'dot -Txdot /tmp/a.dot > /tmp/a.xdot'")

        parser = XDotParser(open("/tmp/a.xdot").read().encode('utf-8'), self, dot_writer.bag)
        return parser.parse()

    def _id(self, fd, system):
        return _id(fd, system)

    def _format(self, fd):
       return _format(fd)