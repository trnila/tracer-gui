import itertools
import json
import os
import socket
from io import StringIO

from PyQt5.QtWidgets import QTableWidgetItem

import maps
import utils
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


def evalme(query, **kwargs):
    descriptor = kwargs['descriptor'] if 'descriptor' in kwargs else None

    class base:
        def __init__(self, s):
            self.str = s

        def matches(self, str2):
            return self.str == str2

    class contains(base):
        def matches(self, str2):
            return self.str in str2

    class endswith(base):
        def matches(self, str2):
            return str2.endswith(self.str)

    class startswith(base):
        def matches(self, str2):
            return str2.startswith(self.str)

    def is_file(s=contains("")):
        if isinstance(s, str):
            s = base(s)

        return descriptor and descriptor['type'] == 'file' and s.matches(descriptor['path'])

    a = {
        "process": None,
        "descriptor": None,
        **kwargs,
        "is_file": is_file,
        "contains": contains,
        "endswith": endswith,
        "startswith": startswith
    }
    return eval(query, a)


class Action:
    def __init__(self, system):
        self.system = system

    def generate(self, dot_writer):
        pass

    def gui(self, window):
        pass

    def apply_filter(self, query):
        print("Warn", self)
        return False


class ProcessCreated(Action):
    def __init__(self, system, process, parent=None):
        super().__init__(system)
        self.process = process
        self.parent = parent

    def generate(self, dot_writer):
        dot_writer.write_node(self.process['pid'], self.process['executable'], data=self)

        if self.parent:
            dot_writer.write_edge(self.parent['pid'], self.process['pid'])

    def gui(self, window):
        window.content.setText(' '.join(self.process['arguments']))

        window.environments.setRowCount(len(self.process['env']))
        window.environments.clearContents()

        row = 0
        for key, value in self.process['env'].items():
            window.environments.setItem(row, 0, QTableWidgetItem(key))
            window.environments.setItem(row, 1, QTableWidgetItem(value))
            row += 1

    def apply_filter(self, query):
        return evalme(query, process=self.process, parent=self.parent)

    def __repr__(self):
        return "[%d] created %d" % (self.process['pid'], self.parent['pid'] if self.parent else 0)


class Res(Action):
    def __init__(self, resource):
        self.resource = resource

    def generate(self, dot_writer):
        dot_writer.write_node(_id(self.resource, self.resource.process.system), _format(self.resource))

    def apply_filter(self, query):
        return evalme(query, descriptor=self.resource)

    def __repr__(self):
        return "[%d] res" % self.resource.process['pid']


class Des(Action):
    def __init__(self, descriptor):
        super().__init__(None)
        self.descriptor = descriptor

    def _get_file_id(self):
        raise NotImplementedError()

    def generate(self, dot_writer):
        raise NotImplementedError()

    def gui(self, window):
        content = self.descriptor.process.system.read_file(self._get_file_id()).decode('utf-8', 'ignore')

        str = ""
        start = 0
        colors = ['red', 'blue']
        col = 0
        for operation in self.descriptor['operations']:
            if operation['type'] in ['read', 'write']:
                backtrace = "\n".join([fn['location'] for fn in operation['backtrace']]).strip()
                str += '<span style="color:%s" title="%s">%s</span>' % (
                    colors[col % len(colors)],
                    backtrace,
                    content[start:start + operation['size']]
                )
                start += operation['size']
                col += 1

        str += content[start:]

        window.content.setText(str.replace("\n", "<br>"))

    def apply_filter(self, filter):
        return evalme(filter, descriptor=self.descriptor)


class ReadDes(Des):
    def generate(self, dot_writer):
        dot_writer.write_edge(
            _id(self.descriptor, self.descriptor.process.system),
            self.descriptor.process['pid'],
            data=self,
        )

    def _get_file_id(self):
        return self.descriptor['read_content']

    def __repr__(self):
        return "[%d] read: %s" % (self.descriptor.process['pid'], self.descriptor)


class WriteDes(Des):
    def generate(self, dot_writer):
        dot_writer.write_edge(
            self.descriptor.process['pid'],
            _id(self.descriptor, self.descriptor.process.system),
            data=self,
        )

    def _get_file_id(self):
        return self.descriptor['write_content']

    def __repr__(self):
        return "[%d] write: %s" % (self.descriptor.process['pid'], self.descriptor)


class Mmap(Des):
    def generate(self, dot_writer):
        dot_writer.write_biedge(
            self.descriptor.process['pid'],
            _id(self.descriptor, self.descriptor.process.system),
            data=self
        )

    def gui(self, window):
        file = open(self.descriptor['path'], 'rb')
        def _format_mmap(item):
            def r(range):
                start, stop = range.split('-', 2)
                start = int(start, 16) - item['address']
                stop = int(stop, 16) - item['address']

                file.seek(start)
                return file.read(stop - start).decode('utf-8', 'ignore')

            return "0x%X - 0x%X (%s) %s %s %s" % (
                item['address'],
                item['address'] + item['length'],
                utils.format_bytes(item['length']),
                maps.mmap_prots.format(item['prot']),
                maps.mmap_maps.format(item['flags']),
                [r(i) for i in item['regions']]
            )

        value = "\n".join(map(_format_mmap, self.descriptor['mmap']))
        window.content.setText(value)

    def __repr__(self):
        return "[%d] mmap" % self.descriptor.process['pid']


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

    def load(self, path):
        with open(os.path.join(path, 'data.json')) as file:
            self.systems.append(System(path, json.load(file)))

    def get_system(self, id):
        return self.systems[id]

    def create_graph(self, filter=None):
        str = StringIO()
        dot_writer = DotWriter(str)
        dot_writer.begin()

        # isinstance(action, ReadDes) and "path" in action.descriptor and action.descriptor["path"].startswith("/etc/")
        def filt(action):
            import parser
            try:
                code = parser.expr(filter).compile()
                if action.apply_filter(code):
                    action.generate(dot_writer)
            except Exception as e:
                print(e)
                raise e

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
                filt(ProcessCreated(system, process, parent))

                # kills
                for kill in process['kills']:
                    dot_writer.write_edge(pid, kill['pid'], label=maps.signals[kill['signal']])

                for name in process['descriptors']:
                    #if name['type'] == 'socket' and 'server' in name and not name['server'] and len(self.systems) > 1:
                     #   continue

                    filt(Res(name))

                    #if 'server' in name and name['server']:
                    #    dot_writer.write_edge(pid, self._id(name, system))

                    if 'read_content' in name:
                        filt(ReadDes(name))

                    if 'write_content' in name:
                        filt(WriteDes(name))

                    if 'mmap' in name and len(name['mmap']):
                        filt(Mmap(name))

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