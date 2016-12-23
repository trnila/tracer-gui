from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QTableView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from tracergui.widgets.Backtrace import BacktraceWidget


class Model(QAbstractTableModel):
    labels = ['Option', 'Level', 'Value']

    def __init__(self, options):
        super().__init__()
        self.options = options

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.options)

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def data(self, QModelIndex, role=None):
        cols = ['optname', 'level', 'value']

        if role == Qt.CheckStateRole:
            return None
        if role == Qt.DisplayRole:
            return self.options[QModelIndex.row()][cols[QModelIndex.column()]]
        return None

    def headerData(self, p_int, Qt_Orientation, role=None):
        if role == Qt.DisplayRole and Qt_Orientation == Qt.Horizontal:
            return self.labels[p_int]
        return QAbstractTableModel.headerData(self, p_int, Qt_Orientation, role)


class SocketOptionsWidget(QWidget):
    def __init__(self, options):
        super().__init__()
        self.backtrace = BacktraceWidget()

        table = QTableView()
        table.setModel(Model(options))
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.clicked.connect(self.handle_click)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(table)
        self.layout().addWidget(self.backtrace)

    def handle_click(self, index):
        backtrace = index.model().options[index.row()]['backtrace']
        self.backtrace.new_backtrace.emit(backtrace)
