from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from widgets.Backtrace import BacktraceWidget


class InfoWidget(QWidget):
    def __init__(self, descriptor, graph):
        super().__init__()
        self.descriptor = descriptor
        self.graphWidget = graph

        text = QTextBrowser()
        text.anchorClicked.connect(self.anchor_clicked)

        self.backtrace = BacktraceWidget()

        items = [
            # 'Mode: ' + open_modes.format(descriptor['mode']),
            "Opened in: <a href='#show_proc'>%s</a> %s" % (
                descriptor['opened_pid'],
                "(<a href='#backtrace'>Show backtrace</a>)" if not self.backtrace.is_empty(
                    descriptor['backtrace']) else ""
            )
        ]
        text.setHtml("<br>".join(items))

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(text)
        self.layout().addWidget(self.backtrace)

    def anchor_clicked(self, url):
        if url.toString() == "#backtrace":
            if self.backtrace.isHidden():
                self.backtrace.new_backtrace.emit(self.descriptor['backtrace'])
            else:
                self.backtrace.hide()
        else:
            self.graphWidget.showPid.emit(self.descriptor['opened_pid'])
