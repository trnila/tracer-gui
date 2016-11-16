import base64
import copy
import json
import os
import socket
from io import StringIO

from DotWriter import DotWriter
from actions.Mmap import Mmap
from actions.ProcessAction import ProcessAction
from actions.ProcessCreated import ProcessCreated
from actions.ReadDes import ReadDes
from actions.Res import Res
from actions.WriteDes import WriteDes
from dot.parser import XDotParser
from objects.System import System


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
