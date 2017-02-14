from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from tracergui import maps
from tracergui.widgets.backtrace import BacktraceWidget


class InfoWidget(QWidget):
    def __init__(self, descriptor, graph):
        super().__init__()
        self.descriptor = descriptor
        self.graphWidget = graph

        text = QTextBrowser()
        text.anchorClicked.connect(self.anchor_clicked)

        self.backtrace = BacktraceWidget()

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
            items.append('Mode: %s' % maps.open_modes.format(descriptor['mode']))

        if 'domain' in descriptor:
            items.append("Domain: %s" % maps.domains.get(descriptor['domain']))
            items.append("Remote: %s" % descriptor['remote'])
            items.append("Type: %s" % maps.socket_types.get(descriptor['socket_type']))

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
