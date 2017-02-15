import html

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QWidget, QTextBrowser, QVBoxLayout

from tracergui.widgets.backtrace import BacktraceWidget


class TextView(QWidget):
    def __init__(self, backtrace):
        super().__init__()
        self.backtraces = []

        self.browser = QTextBrowser()
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
        self.browser.setText(text.replace("\n", "<br>"))

    def handle_click(self, url):
        self.browser.setSource(QUrl(""))  # dont redirect
        self.backtrace_widget.new_backtrace.emit(self.backtraces[int(url.toString())])
