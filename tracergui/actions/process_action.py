from tracergui.actions.action import Action
from tracergui.evaluator import evalme


class ProcessAction(Action):
    def __init__(self, system, process):
        super().__init__(system)
        self.process = process

    def generate(self, dot_writer):
        dot_writer.write_node(self.process['pid'], self.process['executable'], data=self, shape='rect')

    def apply_filter(self, query):
        return evalme(query, process=self.process)
