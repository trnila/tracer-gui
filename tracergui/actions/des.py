from PyQt5.QtWidgets import QTextEdit

from tracergui.actions.action import Action
from tracergui.evaluator import evalme
from tracergui.objects.backtrace import Frame, Backtrace
from tracergui.widgets.hex import HexView
from tracergui.widgets.info import InfoWidget
from tracergui.widgets.socket_options import SocketOptionsWidget
from tracergui.widgets.text_view import TextBacktraceView


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
        for edge in graph.hashes[self.hash]:
            try:
                if self.graphic_elem != edge.graphic_elem:
                    edge.graphic_elem.setSecondFocus(True)
                    edge.graphic_elem.setSelected(True)
            except:
                pass  # some elements may not have graphic_elem

        if self.content:
            edit = QTextEdit()
            edit.setText(self.content)
            window.addTab(edit, "Content")
            return

        content = self.descriptor.process.system.read_file(self._get_file_id()).decode('utf-8', 'ignore')

        edit = TextBacktraceView(self.get_backtrace(content),
                                 self.descriptor.process.system.get_resource_path(self._get_file_id()))
        if 'sockopts' in self.descriptor:
            window.addTab(SocketOptionsWidget(self.descriptor['sockopts']), "Socket options")
        window.addTab(edit, "Content")
        # self.create_hexview(content, window)
        window.addTab(InfoWidget(self.descriptor, graph), "Info")

    def create_hexview(self, content, window):
        operations = self.get_backtrace(content)
        window.addTab(HexView(operations), "Hex")

    def get_backtrace(self, content):
        start = 0
        backtrace = Backtrace()

        for operation in self.descriptor['operations']:
            if operation['type'] == self.type():
                frame = Frame(content[start:start + operation['size']])
                frame.backtrace = operation.get('backtrace', [])
                backtrace.add_frame(frame)

                start += operation['size']
        return backtrace

    def apply_filter(self, query):
        return evalme(query, descriptor=self.descriptor) and evalme(query, process=self.descriptor.process)
