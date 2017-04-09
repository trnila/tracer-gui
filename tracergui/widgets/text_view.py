import atexit
import html
import subprocess
import tempfile

from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QWidget, QTextBrowser, QVBoxLayout

from tracergui import settings
from tracergui.widgets.backtrace import BacktraceWidget


class ProgramExecutor:
    def __init__(self):
        atexit.register(self.collect)
        self.temps = []

    def collect(self):
        self.temps = [item for item in self.temps if item[0].poll() is None and item[0].returncode is None]

    def run(self, command, file=False, content=False):
        self.collect()

        temp = None
        if not file:
            temp = tempfile.NamedTemporaryFile()
            temp.write(content)
            temp.flush()
            file = temp.name

        # TODO: do proper escaping
        escaped_cmd = command.replace("%path%", file)
        print("executing {}".format(escaped_cmd))
        child = subprocess.Popen(escaped_cmd, shell=True)

        if temp:
            self.temps.append((child, temp))


class TextView(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.customContextMenuRequested.connect(self._custom_menu)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.file = None
        self.raw_content = None
        self.executor = ProgramExecutor()

    def set_content(self, content, file=None):
        self.raw_content = content

        if isinstance(content, bytes):
            content = content.decode('utf-8', 'replace')

        self.setText(content)
        self.file = file

    def _custom_menu(self, point):
        def open_editor(command):
            def fn():
                self.executor.run(command, self.file, self.raw_content)

            return fn

        menu = QMenu()

        actions = []
        for name, command in settings.EDITORS.items():
            act = QAction("Open with {}".format(name))
            act.triggered.connect(open_editor(command))
            menu.addAction(act)
            actions.append(act)  # XXX: why it is overwritten if not appended to list?

        menu.exec_(self.mapToGlobal(point))


class TextBacktraceView(QWidget):
    TAB_SIZE = 2

    def __init__(self, backtrace, file=None):
        super().__init__()
        self.file = file

        self.backtraces = []

        self.browser = TextView()
        self.browser.anchorClicked.connect(self.handle_click)
        self.backtrace_widget = BacktraceWidget()

        lay = QVBoxLayout()
        lay.addWidget(self.browser)
        lay.addWidget(self.backtrace_widget)
        self.setLayout(lay)

        self.set_frames(backtrace)

    def set_frames(self, backtrace):
        text = ""
        colors = ['red', 'blue']
        col = 0
        i = 0
        for frame in backtrace.frames:
            self.backtraces.append(frame.backtrace)
            text += '<a href="%d" style="color:%s;text-decoration:none;">%s</a>' % (
                i,
                colors[col % len(colors)],
                html.escape(frame.content).replace('\t', ' ' * self.TAB_SIZE).replace(' ', '&nbsp;')
            )
            col += 1
            i += 1
        self.browser.set_content(text.replace("\n", "<br>"), self.file)

    def handle_click(self, url):
        self.browser.setSource(QUrl(""))  # dont redirect
        self.backtrace_widget.new_backtrace.emit(self.backtraces[int(url.toString())])
