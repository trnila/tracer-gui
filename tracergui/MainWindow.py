import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from tracergui.TracedData import TracedData, FilterException
from tracergui.widgets.GraphWidget import GraphWidget

DEFAULT_FILTER = "process or is_file2() or (descriptor and descriptor['type'] == 'socket')"


class MainWindow(QtWidgets.QMainWindow):
    filter = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = TracedData()
        for directory in sys.argv[1:]:
            self.data.load(directory)

        self.graph = GraphWidget(self.data)

        central = QWidget()
        central.setLayout(QVBoxLayout())
        self.setCentralWidget(central)

        self.filterGui = QLineEdit()
        self.filterGui.returnPressed.connect(lambda: self.filter.emit(self.filterGui.text()))

        self.tab = QTabWidget()
        self.tab.setMinimumHeight(200)

        central.layout().addWidget(self.filterGui)

        splitter = QSplitter(Qt.Vertical)
        central.layout().addWidget(splitter)
        splitter.addWidget(self.graph)
        splitter.addWidget(self.tab)

        self.filter.connect(self.filter_handler)
        self.filter.emit(DEFAULT_FILTER)
        self.graph.onSelected.connect(self.display)

    def display(self, base):
        self.tab.clear()
        if getattr(base, 'action', None):
            base.action.gui(self.tab, self.graph)

    def filter_handler(self, text):
        self.filterGui.setText(text)
        try:
            self.graph.apply_filter(text)
        except FilterException as e:
            QMessageBox().critical(self, "Filter error", e.message)
