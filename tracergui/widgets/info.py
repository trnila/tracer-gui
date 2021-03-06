from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from tracergui.widgets.backtrace import BacktraceWidget


class InfoWidget(QWidget):
    def __init__(self, descriptor, graph):
        super().__init__()
        self.descriptor = descriptor
        self.graphWidget = graph

        self.browser = QTextBrowser()
        self.browser.anchorClicked.connect(self.anchor_clicked)

        self.backtrace = BacktraceWidget()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.browser)
        self.layout().addWidget(self.backtrace)

        self.set_descriptor(descriptor)

    def set_descriptor(self, descriptor):
        items = []
        if 'fd' in descriptor:
            items.append("fd: {}".format(descriptor['fd']))
        if 'opened_pid' in descriptor:
            items.append("Opened in: <a href='#show_proc'>{pid}</a> {backtrace}".format(
                pid=descriptor['opened_pid'],
                backtrace="(<a href='#backtrace'>Show backtrace</a>)" if not self.backtrace.is_empty(
                    descriptor['backtrace']) else ""
            ))
        if 'mode' in descriptor:
            items.append('Mode: {}'.format("|".join(descriptor['mode'])))
        if 'flags' in descriptor:
            items.append('Flags: {}'.format("|".join(descriptor['flags'])))
        if 'domain' in descriptor:
            items.append("Domain: %s" % descriptor['domain'])
            items.append("Remote: %s" % descriptor['remote'])
            items.append("Type: %s" % descriptor['socket_type'])
        self.browser.setHtml("<br>".join(items))

    def anchor_clicked(self, url):
        if url.toString() == "#backtrace":
            if self.backtrace.isHidden():
                self.backtrace.new_backtrace.emit(self.descriptor['backtrace'])
            else:
                self.backtrace.hide()
        else:
            self.graphWidget.showPid.emit(self.descriptor['opened_pid'])
