import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit

from TracedData import TracedData
from nodes import Base, Process, Edge, Ellipse


class Widget(QtWidgets.QGraphicsView):
    onSelected = pyqtSignal(Base)

    def __init__(self, data):
        super().__init__()

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setMouseTracking(True)

        self.p = p = QGraphicsScene(self)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing)

        self.setScene(self.p)
        self.show()

        self.graph = data.create_graph()
        for type in [self.graph.shapes, self.graph.nodes, self.graph.edges]:
            for node in type:
                if isinstance(node, QGraphicsItem):
                    p.addItem(node)

    def wheelEvent(self, evt):
        scale = 1.2 if evt.angleDelta().y() > 0 else 0.8

        self.scale(scale, scale)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # def mousePressEvent(self, QMouseEvent):
        #	item = self.itemAt(QMouseEvent.x(), QMouseEvent.y())
        #	if isinstance(item, QAbstractGraphicsShapeItem):
        #		item.setBrush(QColor(255, 0, 0, 128))

    def mousePressEvent(self, QMouseEvent):
        super().mousePressEvent(QMouseEvent)
        item = self.itemAt(QMouseEvent.x(), QMouseEvent.y())

        while item and not isinstance(item, Base):
            item = item.parentItem()

        if item:
            print(item)
            self.onSelected.emit(item)


class ExampleApp(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)

        data = TracedData()

        for dir in sys.argv[1:]:
            data.load(dir)

        graph = Widget(data)
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

        self.filter = QLineEdit(self)
        self.filter.setFixedWidth(self.width())
        self.filter.textChanged.connect(handleFilter)

        dock1 = QDockWidget("Content", self)
        dock1.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        edit = QTextEdit()
        dock1.setWidget(edit)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock1)

        dock2 = QDockWidget("Environments", self)
        dock2.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem("Variable"))
        table.setHorizontalHeaderItem(1, QTableWidgetItem("Value"))
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        dock2.setWidget(table)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock2)

        def display(base):
            if isinstance(base, Process):
                edit.setText(" ".join(base.process['arguments']))
                table.setRowCount(len(base.process['env']))
                table.clearContents()

                row = 0
                for key, value in base.process['env'].items():
                    table.setItem(row, 0, QTableWidgetItem(key))
                    table.setItem(row, 1, QTableWidgetItem(value))
                    row += 1

                dock1.show()
                dock2.show()
            elif isinstance(base, Edge) and base.file:
                edit.setText(base.system.read_file(base.file['content']).decode('utf-8', 'ignore'))
                dock1.show()

        graph.onSelected.connect(display)

    def resizeEvent(self, QResizeEvent):
        self.filter.setFixedWidth(QResizeEvent.size().width())

def main():
    app = QtWidgets.QApplication([])
    window = ExampleApp()
    window.setWindowTitle('GUI')
    window.setFixedSize(1024, 768)
    window.show()
    app.exec_()


main()
