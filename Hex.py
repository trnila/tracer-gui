from PyQt5 import QtCore

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QTextFormat
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


def to_hex(i):
    return hex(ord(i)).replace('0x', '').zfill(2)


colors = [QtCore.Qt.red, QtCore.Qt.blue]


class Single:
    def __init__(self, content, backtrace=[]):
        self.content = content
        self.backtrace = backtrace


class MyItem(QTableWidgetItem):
    def __init__(self, text, item):
        super().__init__(text)
        self.item = item


class MYHex(QWidget):
    def __init__(self, contents):
        super().__init__()

        def fn(row, col):
            if col < 16:
                index = table.model().index(row, col + 16)
            else:
                index = table.model().index(row, col - 16)

            cell = table.item(row, col)
            if cell:
                locs.new_backtrace.emit(cell.item.backtrace)
                table.selectionModel().select(index, QItemSelectionModel.Select)

        locs = BacktraceWidget()
        table = QTableWidget()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(table)
        self.layout().addWidget(locs)

        table.setColumnCount(32)
        table.horizontalHeader().setDefaultSectionSize(25)
        table.verticalHeader().setDefaultSectionSize(25)
        table.setRowCount(52)
        table.cellClicked.connect(fn)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        table.setShowGrid(False)
        table.setSelectionMode(QAbstractItemView.SingleSelection)

        row = 0
        col = 0
        color_index = 0
        for content in contents:
            for i in content.content:
                table.setItem(row, col, self.create_item(to_hex(i), content, color_index))
                table.setItem(row, col + 16, self.create_item(i if i.isprintable() else '.', content, color_index))
                col += 1
                if col >= 16:
                    col = 0
                    row += 1
            color_index += 1

    def create_item(self, i, y, index):
        item = MyItem(i, y)
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        item.setForeground(colors[index % 2])
        return item


class BacktraceWidget(QWidget):
    new_backtrace = pyqtSignal(list)
    show_source = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.show_sources = True

        self.new_backtrace.connect(self._handle_new_backtrace)
        self.show_source.connect(self._handle_show_source)

        self.locations = QListWidget()
        self.locations.itemClicked.connect(self._handle_location_click)
        self.locations.setFixedWidth(200)

        self.text = QTextEdit(self)
        self.text.setParent(self)
        self.text.setReadOnly(True)

        splitter = QSplitter(self)
        splitter.addWidget(self.locations)
        splitter.addWidget(self.text)

        lay = QVBoxLayout()
        lay.addWidget(splitter)
        self.setLayout(lay)

    def _handle_new_backtrace(self, backtrace):
        self.locations.clear()
        for i in backtrace:
            if not self.show_sources or (i['location'] and self.show_sources):
                self.locations.addItem(i['location'] if i['location'] else hex(i['ip']))

        self.show_source.emit(0)

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
