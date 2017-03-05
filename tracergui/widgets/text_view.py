import html
import subprocess

from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QWidget, QTextBrowser, QVBoxLayout

from tracergui import settings
from tracergui.widgets.backtrace import BacktraceWidget


class TextView(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.customContextMenuRequested.connect(self._custom_menu)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.file = None

    def set_content(self, content, file=None):
        self.setText(content)
        self.file = file

    def _custom_menu(self, point):
        def open_editor(command):
            def fn():
                # TODO: do proper escaping
                escaped_cmd = command.replace("%path%", self.file)
                print("executing {}".format(escaped_cmd))
                subprocess.Popen(escaped_cmd, shell=True)

            return fn

        menu = QMenu()

        if self.file:
            actions = []
            for name, command in settings.EDITORS.items():
                act = QAction("Open with {}".format(name))
                act.triggered.connect(open_editor(command))
                menu.addAction(act)
                actions.append(act)  # XXX: why it is overwritten if not appended to list?

        menu.exec_(self.mapToGlobal(point))


class TextBacktraceView(QWidget):
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
            text += '<a href="%d" style="color:%s">%s</a>' % (
                i,
                colors[col % len(colors)],
                html.escape(frame.content)
            )
            col += 1
            i += 1
        self.browser.set_content(text.replace("\n", "<br>"), self.file)

    def handle_click(self, url):
        self.browser.setSource(QUrl(""))  # dont redirect
        self.backtrace_widget.new_backtrace.emit(self.backtraces[int(url.toString())])
