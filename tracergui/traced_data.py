import base64
import copy
import json
import os
import parser
import subprocess
from io import StringIO

from tracergui.actions.mmap import Mmap
from tracergui.actions.process_created import ProcessCreated
from tracergui.actions.read_des import ReadDes
from tracergui.actions.res import Res
from tracergui.actions.signal import Signal
from tracergui.actions.write_des import WriteDes
from tracergui.dot.parser import XDotParser
from tracergui.dot_writer import DotWriter
from tracergui.objects.system import System


class FilterException(Exception):
    def __init__(self, message):
        self.message = message


class TracedData:
    def __init__(self):
        self.graphviz = Graphviz()

    def load(self, path):
        self.graphviz.load(path)

    def gen_graph(self, dot_writer):
        p = subprocess.Popen(["dot", "-Txdot"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(dot_writer.get_content().encode('utf-8'))
        if p.returncode != 0:
            raise Exception(stderr.decode('utf-8'))

        parser = XDotParser(stdout, self, dot_writer.bag)
        return parser.parse()

    def create_graph(self, filter=None):
        dot_writer = self.graphviz.create_graph(filter)

        return self.gen_graph(dot_writer)


class Graphviz:
    def __init__(self):
        self.systems = []

    def load(self, path):
        with open(os.path.join(path, 'data.json')) as file:
            self.systems.append(System(path, json.load(file)))

    def create_graph(self, filter=None):
        self.filter = "True" if not filter else filter

        roots = [self.create_system(system) for system in self.systems]

        str = StringIO()
        dot_writer = DotWriter(str)
        dot_writer.begin()

        self.create_network(dot_writer, roots)

        for i, root in enumerate(roots):
            dot_writer.begin_subgraph("node #%d" % i)
            self.write_system(root, dot_writer)
            dot_writer.end_subgraph()

        dot_writer.end()

        return dot_writer

    def create_network(self, dot_writer, roots):
        dot_writer.begin_subgraph("NETWORK")
        for i, root in enumerate(roots):
            def g(proc):
                for process in proc.edges:
                    g(process)

                for res in proc.res:
                    if (isinstance(res, ReadDes) or isinstance(res, WriteDes)) and res.descriptor[
                        'type'] == 'socket' and res.descriptor['domain'] in ['AF_INET', 'AF_INET6']:
                        if self.test(res.des):
                            res.des.generate(dot_writer)

            g(root)
        dot_writer.end_subgraph()

    def create_system(self, system):
        pids = {}
        for pid, process in system.processes.items():
            parent = system.get_process_by_pid(process['parent']) if process['parent'] > 0 else None

            pids[process['pid']] = ProcessCreated(system, process, parent)

            if not parent:
                root = pids[process['pid']]

            # kills
            for kill in process['kills']:
                pids[process['pid']].res.append(Signal(pid, kill['pid'], kill['signal'], system))

            for name in process['descriptors']:
                if name['type'] == 'socket' and name['socket_type'] == 'SOCK_DGRAM' and name[
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

                if 'mmap' in name and name['mmap']:
                    x = Mmap(name)
                    x.process = process
                    x.des = Res(name)
                    pids[process['pid']].res.append(x)

        for pid, process in system.processes.items():
            if process['parent'] != 0:
                pids[process['parent']].edges.append(pids[process['pid']])
        return root

    def test(self, node):
        try:
            code = parser.expr(self.filter).compile()
            return node.apply_filter(code)
        except Exception as e:
            raise FilterException(e.args[0])

    def write_system(self, process, dot_writer):
        if self.test(process):
            process.generate(dot_writer)

            for res in process.res:
                if self.test(res):
                    # TODO: ?
                    if getattr(res, 'des', None):
                        res.des.generate(dot_writer)
                    res.generate(dot_writer)

        for proc in process.edges:
            if self.test(proc):
                self.write_system(proc, dot_writer)
