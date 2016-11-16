import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from GraphWidget import GraphWidget
from TracedData import TracedData, FilterException

DEFAULT_FILTER = "process or is_file2()"
DEFAULT_FILTER = "process or descriptor and descriptor['type'] == 'socket'"
DEFAULT_FILTER = "1"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        data = TracedData()
        for directory in sys.argv[1:]:
            data.load(directory)

        central = QWidget()
        self.setCentralWidget(central)

        graph = GraphWidget(data)

        def handle_enter():
            try:
                graph.apply_filter(self.filter.text())
            except FilterException as e:
                QMessageBox().critical(self, "Filter error", e.message)

        self.filter = QLineEdit()
        self.filter.returnPressed.connect(handle_enter)
        self.filter.setText(DEFAULT_FILTER)
        handle_enter()

        tab = QTabWidget()
        tab.setMaximumHeight(200)

        layout = QVBoxLayout()
        central.setLayout(layout)
        layout.addWidget(self.filter)
        layout.addWidget(graph)
        layout.addWidget(tab)

        def display(base):
            tab.clear()
            if getattr(base, 'action', None):
                base.action.gui(tab)

        graph.onSelected.connect(display)
