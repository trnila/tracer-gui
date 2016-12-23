from Evaluator import evalme
from PyQt5.QtWidgets import QTextEdit
from actions.Action import Action
from objects.Backtrace import Frame, Backtrace
from widgets.Hex import HexView
from widgets.InfoWidget import InfoWidget
from widgets.TextView import TextView

from tracergui.widgets.SocketOptionsWidget import SocketOptionsWidget


class Des(Action):
    def __init__(self, descriptor):
        super().__init__(None)
        self.descriptor = descriptor
        self.content = None

    def _get_file_id(self):
        raise NotImplementedError()

    def generate(self, dot_writer):
        raise NotImplementedError()

    def type(self):
        raise NotImplementedError()

    def gui(self, window, graph):
        if self.content:
            edit = QTextEdit()
            edit.setText(self.content)
            window.addTab(edit, "Content")
            return

        content = self.descriptor.process.system.read_file(self._get_file_id()).decode('utf-8', 'ignore')

        edit = TextView(self.get_backtrace(content))
        window.addTab(InfoWidget(self.descriptor, graph), "Info")
        if 'sockopts' in self.descriptor:
            window.addTab(SocketOptionsWidget(self.descriptor['sockopts']), "Socket options")
        window.addTab(edit, "Content")
        self.create_hexview(content, window)

    def create_hexview(self, content, window):
        operations = self.get_backtrace(content)
        window.addTab(HexView(operations), "Hex")

    def get_backtrace(self, content):
        start = 0
        backtrace = Backtrace()

        for operation in self.descriptor['operations']:
            if operation['type'] == self.type():
                frame = Frame(content[start:start + operation['size']])
                frame.backtrace = operation['backtrace']
                backtrace.add_frame(frame)

                start += operation['size']
        return backtrace

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor) and evalme(query, process=self.descriptor.process)
