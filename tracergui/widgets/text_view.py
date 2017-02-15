import html

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QWidget, QTextBrowser, QVBoxLayout

from tracergui.widgets.backtrace import BacktraceWidget


class TextView(QWidget):
    def __init__(self, backtrace):
        super().__init__()
        self.backtraces = []

        def handle_click(url):
            browser.setSource(QUrl(""))  # dont redirect
            backtraceWidget.new_backtrace.emit(self.backtraces[int(url.toString())])

        backtraceWidget = BacktraceWidget()

        str = ""
        colors = ['red', 'blue']
        col = 0
        i = 0
        for frame in backtrace.frames:
            self.backtraces.append(frame.backtrace)
            str += '<a href="%d" style="color:%s">%s</a>' % (
                i,
                colors[col % len(colors)],
                html.escape(frame.content)
            )
            col += 1
            i += 1

        browser = QTextBrowser()
        browser.setText(str.replace("\n", "<br>"))
        browser.anchorClicked.connect(handle_click)

        lay = QVBoxLayout()
        lay.addWidget(browser)
        lay.addWidget(backtraceWidget)
        self.setLayout(lay)
