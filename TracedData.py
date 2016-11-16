import base64
import copy
import itertools
import json
import os
import socket
from io import StringIO

from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit

import maps
import utils
from DotWriter import DotWriter
from Evaluator import evalme
from dot.parser import XDotParser


class Action:
    def __init__(self, system):
        self.system = system
        self.edges = []
        self.res = []

    def generate(self, dot_writer):
        pass

    def gui(self, window):
        pass

    def apply_filter(self, query):
        raise NotImplemented


class ProcessCreated(Action):
    def __init__(self, system, process, parent=None):
        super().__init__(system)
        self.process = process
        self.parent = parent

    def generate(self, dot_writer):
        dot_writer.write_node(self.process['pid'], self.process['executable'], data=self, shape='rect')
        dot_writer.write_edge(self.parent['pid'], self.process['pid'])

    def gui(self, window):
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem("Variable"))
        table.setHorizontalHeaderItem(1, QTableWidgetItem("Value"))
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setRowCount(len(self.process['env']))

        cmdline = QTextEdit()
        cmdline.setPlainText(' '.join(self.process['arguments']))

        row = 0
        for key, value in self.process['env'].items():
            table.setItem(row, 0, QTableWidgetItem(key))
            table.setItem(row, 1, QTableWidgetItem(value))
            row += 1

        window.addTab(cmdline, "Command")
        window.addTab(table, "Environments")

    def apply_filter(self, query):
        return evalme(query, process=self.process)

    def __repr__(self):
        return "[%d] created %d" % (self.process['pid'], self.parent['pid'] if self.parent else 0)


class ProcessAction(Action):
    def __init__(self, system, process):
        super().__init__(system)
        self.process = process

    def generate(self, dot_writer):
        dot_writer.write_node(self.process['pid'], self.process['executable'], data=self, shape='rect')

    def apply_filter(self, query):
        return evalme(query, process=self.process)

class Res(Action):
    def __init__(self, resource):
        self.resource = resource

    def generate(self, dot_writer):
        dot_writer.write_node(self.resource.get_id(), self.resource.get_label())

    def apply_filter(self, query):
        return evalme(query, descriptor=self.resource) and evalme(query, process=self.resource.process)

    def __repr__(self):
        return "[%d] res" % self.resource.process['pid']


class Des(Action):
    def __init__(self, descriptor):
        super().__init__(None)
        self.descriptor = descriptor
        self.content = None

    def _get_file_id(self):
        raise NotImplementedError()

    def generate(self, dot_writer):
        raise NotImplementedError()

    def gui(self, window):
        if self.content:
            edit = QTextEdit()
            edit.setText(self.content)
            window.addTab(edit, "Content")
            return

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

        edit = QTextEdit()
        edit.setText(str.replace("\n", "<br>"))

        window.addTab(edit, "Content")

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor) and evalme(query, process=self.descriptor.process)


class ReadDes(Des):
    def generate(self, dot_writer):
        dot_writer.write_edge(
            self.descriptor.get_id(),
            self.descriptor.process['pid'],
            data=self,
        )

    def _get_file_id(self):
        return self.descriptor['read_content']

    def __repr__(self):
        return "[%d] read: %s" % (self.descriptor.process['pid'], self.descriptor)

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor, type='read') and evalme(query, process=self.descriptor.process)


class WriteDes(Des):
    def generate(self, dot_writer):
        dot_writer.write_edge(
            self.descriptor.process['pid'],
            self.descriptor.get_id(),
            data=self,
        )

    def _get_file_id(self):
        return self.descriptor['write_content']

    def __repr__(self):
        return "[%d] write: %s" % (self.descriptor.process['pid'], self.descriptor)

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor, type='write') and evalme(query,
                                                                                  process=self.descriptor.process)


class Mmap(Des):
    def generate(self, dot_writer):
        dot_writer.write_biedge(
            self.descriptor.process['pid'],
            self.descriptor.get_id(),
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

        edit = QTextEdit()
        edit.setText(value)

        window.addTab(edit, "Content")

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor, type='mmap') and evalme(query, process=self.descriptor.process)

    def __repr__(self):
        return "[%d] mmap" % self.descriptor.process['pid']


class Object:
    def get_id(self):
        raise NotImplemented

    def get_label(self):
        raise NotImplemented


class Descriptor(Object):
    def __init__(self, process, data):
        self.data = data
        self.process = process

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

    def get_id(self):
        if self['type'] == 'file':
            return "%s_%s" % (self.process.system.resource_path, self['path'])

        if self['type'] == 'pipe':
            return "%s_%s" % (id(self.process.system), self['pipe_id'])

        if self['type'] == 'socket' and self['domain'] in [socket.AF_INET, socket.AF_INET6]:
            try:
                parts = sorted([
                    self['local']['address'],
                    str(self['local']['port']),
                    self['remote']['address'],
                    str(self['remote']['port']),
                ])

                return "socket_%s" % (":".join(parts))
            except:
                pass

        return self.get_label()

    def get_label(self):
        if self['type'] == 'socket':
            if self['domain'] == socket.AF_UNIX:
                return "unix:%s" % (self['remote'])

            if self['domain'] in [socket.AF_INET, socket.AF_INET6] and self['local']:  # TODO: quickfix
                if self['remote'] is None:
                    return "%s:%d" % (self['local']['address'], self['local']['port'])

                return "%s:%d\\n<->\\n%s:%d" % (
                    self['local']['address'], self['local']['port'],
                    self['remote']['address'], self['remote']['port']
                )
            return "socket: %s #%s" % (self['domain'], self['socket_id'])

        if self['type'] == 'file':
            return self['path']

        if self['type'] == 'pipe':
            return 'pipe: %d' % self['pipe_id']


class Process(Object):
    def __init__(self, system, data, parent=None):
        self.system = system
        self.data = data
        self.parent = parent

        self.data['descriptors'] = [Descriptor(self, i) for i in self.data['descriptors']]

    def __getitem__(self, item):
        return self.data[item]


class System:
    def __init__(self, resource_path, data):
        self.processes = {}
        self.resource_path = resource_path

        for id, process in data.items():
            self.processes[int(id)] = Process(self, process)

        for id, process in data.items():
            if process['parent']:
                self.get_process_by_pid(int(id)).parent = self.get_process_by_pid(int(process['parent']))

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
        self.filter = filter

        roots = [self.create_system(system) for system in self.systems]

        str = StringIO()
        dot_writer = DotWriter(str)
        dot_writer.begin()

        dot_writer.begin_subgraph("NETWORK")
        for i, root in enumerate(roots):
            def g(proc):
                for process in proc.edges:
                    g(process)

                for res in proc.res:
                    if (isinstance(res, ReadDes) or isinstance(res, WriteDes)) and res.descriptor[
                        'type'] == 'socket' and res.descriptor['domain'] in [
                        socket.AF_INET, socket.AF_INET6]:
                        if self.test(res.des):
                            res.des.generate(dot_writer)

            g(root)

        dot_writer.end_subgraph()

        for i, root in enumerate(roots):
            dot_writer.begin_subgraph("node #%d" % i)
            self.doit(root, dot_writer)
            dot_writer.end_subgraph()

        dot_writer.end()

        return self.gen_graph(dot_writer, str)

    def create_system(self, system):
        pids = {}
        for pid, process in system.processes.items():
            parent = system.get_process_by_pid(process['parent']) if process['parent'] > 0 else None

            if not parent:
                root = ProcessAction(system, process)
                pids[process['pid']] = root
            else:
                proc = ProcessCreated(system, process, parent)
                pids[process['pid']] = proc

            # kills
            # for kill in process['kills']:
            #    dot_writer.write_edge(pid, kill['pid'], label=maps.signals[kill['signal']])

            for name in process['descriptors']:
                # if name['type'] == 'socket' and 'server' in name and not name['server'] and len(self.systems) > 1:
                #   continue

                # filt(Res(name))


                # if 'server' in name and name['server']:
                #    dot_writer.write_edge(pid, self._id(name, system))

                if name['type'] == 'socket' and name['socket_type'] == socket.SOCK_DGRAM and name[
                    'type'] == 'socket' and isinstance(name['local']['address'], list):
                    for addr in name['local']['address']:
                        contents = {
                            "read": {},
                            "write": {}
                        }

                        for read in name['operations']:
                            key = str(read['address']['port']) + read['address']['address']
                            if key not in contents[read['type']]:
                                n = copy.deepcopy(name)
                                n['local']['address'] = addr
                                n.data['remote'] = read['address']
                                x = (WriteDes if read['type'] == 'write' else ReadDes)(n)
                                x.des = Res(n)

                                pids[process['pid']].res.append(x)
                                contents[read['type']][key] = x
                                contents[read['type']][key].content = ''

                            contents[read['type']][key].content += base64.b64decode(read['_']).decode('utf-8')
                else:
                    for key, factory in {'read_content': ReadDes, 'write_content': WriteDes}.items():
                        if key in name:
                            x = factory(name)
                            x.des = Res(name)
                            pids[process['pid']].res.append(x)

                if 'mmap' in name and len(name['mmap']):
                    x = Mmap(name)
                    x.des = Res(name)
                    pids[process['pid']].res.append(x)

        for pid, process in system.processes.items():
            if process['parent'] != 0:
                pids[process['parent']].edges.append(pids[process['pid']])
        return root

    def gen_graph(self, dot_writer, str):
        with open("/tmp/a.dot", "w") as f:
            f.write(str.getvalue())
        import os
        os.system("sh -c 'dot -Txdot /tmp/a.dot > /tmp/a.xdot'")
        parser = XDotParser(open("/tmp/a.xdot").read().encode('utf-8'), self, dot_writer.bag)
        return parser.parse()

    def test(self, node):
        import parser
        try:
            code = parser.expr(self.filter).compile()
            return node.apply_filter(code)
        except Exception as e:
            print(e)
            # raise e

    def doit(self, process, dot_writer):
        if self.test(process):
            process.generate(dot_writer)

            for res in process.res:
                if self.test(res):
                    res.des.generate(dot_writer)
                    res.generate(dot_writer)

        for proc in process.edges:
            if self.test(proc):
                self.doit(proc, dot_writer)
