from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QTextCursor, QTextFormat, QColor
from PyQt5.QtWidgets import QWidget, QListWidget, QTextEdit, QSplitter, QVBoxLayout, QMessageBox, QMenu, QAction

from tracergui.utils import system_open


class BacktraceWidget(QWidget):
    new_backtrace = pyqtSignal(object)
    show_source = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.show_sources = True

        self.new_backtrace.connect(self._handle_new_backtrace)
        self.show_source.connect(self._handle_show_source)

        self.locations = QListWidget()
        self.locations.itemClicked.connect(self._handle_location_click)
        self.locations.setFixedWidth(200)
        self.locations.customContextMenuRequested.connect(self._locations_menu)
        self.locations.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.text = QTextEdit(self)
        self.text.setParent(self)
        self.text.setReadOnly(True)

        splitter = QSplitter(self)
        splitter.addWidget(self.locations)
        splitter.addWidget(self.text)

        lay = QVBoxLayout()
        lay.addWidget(splitter)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)
        self.hide()

    def is_empty(self, backtrace):
        if backtrace:
            for i in backtrace:
                if not self.show_sources or (i['location'] and self.show_sources):
                    return False
        return True

    def _handle_new_backtrace(self, backtrace):
        if not backtrace:
            return

        self.locations.clear()
        for i in backtrace:
            if not self.show_sources or (i['location'] and self.show_sources):
                self.locations.addItem(i['location'] if i['location'] else hex(i['ip']))

        self.show_source.emit(0)
        self.show()

    def _handle_show_source(self, n):
        item = self.locations.item(n)
        if item:
            item.setSelected(True)
            self._handle_location_click(item)

    def _handle_location_click(self, item):
        if item.text()[0] == '/':
            file, line = item.text().split(':')
            try:
                with open(file) as f:
                    content = f.read()

                self.text.setText(content)
                block = self.text.document().findBlockByNumber(int(line) - 1)
                cur = QTextCursor(block)
                cur.select(QTextCursor.LineUnderCursor)

                extra = QTextEdit.ExtraSelection()
                extra.format.setProperty(QTextFormat.FullWidthSelection, True)
                extra.format.setBackground(QColor(Qt.yellow).lighter(160))
                extra.cursor = cur
                self.text.setExtraSelections([extra])

                self.text.setTextCursor(cur)
                self.text.moveCursor(QTextCursor.EndOfLine)
            except IOError as e:
                QMessageBox().critical(self, "Could not open file", "Could not open file %s: %s" % (file, e.strerror))

    def _locations_menu(self, point):
        def open_editor():
            item = self.locations.selectedItems()[0]
            if item:
                file = item.text().split(':')[0]
                if file:
                    system_open(file)

        menu = QMenu()

        act = QAction("Open with system editor")
        act.triggered.connect(open_editor)
        menu.addAction(act)

        menu.exec_(self.mapToGlobal(point))
