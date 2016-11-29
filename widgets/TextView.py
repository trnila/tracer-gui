from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QWidget, QTextBrowser, QVBoxLayout

from widgets.Backtrace import BacktraceWidget


class TextView(QWidget):
    def __init__(self, content, operations):
        super().__init__()
        self.backtraces = []

        def handle_click(url):
            browser.setSource(QUrl(""))  # dont redirect
            backtraceWidget.new_backtrace.emit(self.backtraces[int(url.toString())])

        backtraceWidget = BacktraceWidget()

        str = ""
        start = 0
        colors = ['red', 'blue']
        col = 0
        i = 0
        for operation in operations:
            if operation['type'] in ['read', 'write']:
                self.backtraces.append(operation['backtrace'])
                str += '<a href="%d" style="color:%s">%s</a>' % (
                    i,
                    colors[col % len(colors)],
                    content[start:start + operation['size']]
                )
                start += operation['size']
                col += 1
                i += 1

        str += content[start:]

        browser = QTextBrowser()
        browser.setText(str.replace("\n", "<br>"))
        browser.anchorClicked.connect(handle_click)

        lay = QVBoxLayout()
        lay.addWidget(browser)
        lay.addWidget(backtraceWidget)
        self.setLayout(lay)
