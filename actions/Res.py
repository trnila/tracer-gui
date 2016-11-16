from Evaluator import evalme
from actions.Action import Action


class Res(Action):
    def __init__(self, resource):
        self.resource = resource

    def generate(self, dot_writer):
        dot_writer.write_node(self.resource.get_id(), self.resource.get_label())

    def apply_filter(self, query):
        return evalme(query, descriptor=self.resource) and evalme(query, process=self.resource.process)

    def __repr__(self):
        return "[%d] res" % self.resource.process['pid']
