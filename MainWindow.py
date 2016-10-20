import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QDockWidget, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView

from GraphWidget import GraphWidget
from TracedData import TracedData
from nodes import Ellipse


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        data = TracedData()

        for dir in sys.argv[1:]:
            data.load(dir)

        graph = GraphWidget(data)
        self.setCentralWidget(graph)

        def handleFilter(query):
            for i in graph.graph.nodes:
                i.setVisible(True)
                for nei in i.neighbours:
                    nei.setVisible(True)

            for i in graph.graph.nodes:
                if isinstance(i, Ellipse):
                    if query and query in i.label.toPlainText():
                        i.setVisible(False)
                        for nei in i.neighbours:
                            nei.setVisible(False)

        def handleEnter():
            graph.apply_filter(self.filter.text())

        self.filter = QLineEdit(self)
        self.filter.setFixedWidth(self.width())
        self.filter.textChanged.connect(handleFilter)
        self.filter.returnPressed.connect(handleEnter)

        dock1 = QDockWidget("Content", self)
        dock1.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.content = edit = QTextEdit()
        dock1.setWidget(edit)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock1)

        dock2 = QDockWidget("Environments", self)
        dock2.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        self.environments = table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem("Variable"))
        table.setHorizontalHeaderItem(1, QTableWidgetItem("Value"))
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        dock2.setWidget(table)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock2)

        def display(base):
            edit.setText("")
            if getattr(base, 'action', None):
                base.action.gui(self)

        graph.onSelected.connect(display)

    def resizeEvent(self, QResizeEvent):
        self.filter.setFixedWidth(QResizeEvent.size().width())
