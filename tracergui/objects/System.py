import itertools

from objects.Process import Process


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
