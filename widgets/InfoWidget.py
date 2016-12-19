from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from maps import open_modes
from widgets.Backtrace import BacktraceWidget


class InfoWidget(QWidget):
    def __init__(self, descriptor):
        super().__init__()
        text = QTextBrowser()
        text.anchorClicked.connect(self.anchor_clicked)

        items = [
            'Mode: ' + open_modes.format(descriptor['mode']),
            "Opened in: <a href='#show_proc'>%s</a>" % descriptor['opened_pid'],
            "<a href='#backtrace'>Show backtrace</a>"
        ]
        text.setHtml("<br>".join(items))

        backtrace = BacktraceWidget()
        backtrace.new_backtrace.emit(descriptor['backtrace'])
        backtrace.hide()
        self.backtrace = backtrace

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(text)
        self.layout().addWidget(backtrace)

    def anchor_clicked(self, url):
        if url.toString() == "#backtrace":
            if self.backtrace.isHidden():
                self.backtrace.show()
            else:
                self.backtrace.hide()
