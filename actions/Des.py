from PyQt5.QtWidgets import QTextEdit

from Evaluator import evalme
from Hex import MYHex, Single
from actions.Action import Action


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

        start = 0

        operations = []
        for operation in self.descriptor['operations']:
            if operation['type'] in ['read', 'write']:
                si = Single(content[start:start + operation['size']])
                si.backtrace = operation['backtrace']
                operations.append(si)

                start += operation['size']

        window.addTab(MYHex(operations), "f")

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor) and evalme(query, process=self.descriptor.process)
