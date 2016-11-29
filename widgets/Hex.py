from PyQt5 import QtCore
from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from widgets.Backtrace import BacktraceWidget


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


class HexView(QWidget):
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
