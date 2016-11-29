from PyQt5.QtWidgets import QTextEdit

from Evaluator import evalme
from actions.Action import Action
from widgets.Hex import HexView, Single
from widgets.TextView import TextView


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

        edit = TextView(content, self.descriptor['operations'])
        window.addTab(edit, "Content")
        self.create_hexview(content, window)

    def create_hexview(self, content, window):
        operations = self.gen(content)
        window.addTab(HexView(operations), "Hex")

    def gen(self, content):
        start = 0
        operations = []
        for operation in self.descriptor['operations']:
            if operation['type'] in ['read', 'write']:
                si = Single(content[start:start + operation['size']])
                si.backtrace = operation['backtrace']
                operations.append(si)

                start += operation['size']
        return operations

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor) and evalme(query, process=self.descriptor.process)