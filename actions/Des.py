from PyQt5.QtWidgets import QTextEdit

from Evaluator import evalme
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
