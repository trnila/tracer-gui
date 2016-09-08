import json

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit

from dot.parser import XDotParser
from nodes import Base, Process, Edge


class Widget(QtWidgets.QGraphicsView):
    onSelected = pyqtSignal(Base)

    def __init__(self):
        super().__init__()

        data = json.load(open("/tmp/data.json"))

        str = "digraph A {\n"
        for pid, process in data.items():
            str += "%d [label=\"%s\"];\n" % (int(pid), process['executable'])  # FIXME: escape

            if process['parent'] > 0:
                str += "%d -> %d;\n" % (process['parent'], int(pid))

            for id, name in process['read'].items():
                str += "\"%s\" [label=\"%s\"];\n" % (id, id)  # FIXME: escape
                str += "\"%s\" -> %d;\n" % (id, int(pid))

            for id, name in process['write'].items():
                str += "\"%s\" [label=\"%s\"];\n" % (id, id)  # FIXME: escape
                str += "%d -> \"%s\";\n" % (int(pid), id)

        str += "\n}"

        with open("/tmp/a.dot", "w") as f:
            f.write(str)

        import os
        os.system("sh -c 'dot -Txdot /tmp/a.dot > /tmp/a.xdot'")

        parser = XDotParser(open("/tmp/a.xdot").read().encode('utf-8'))
        self.graph = parser.parse()

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setMouseTracking(True)

        self.p = p = QGraphicsScene(self)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing)

        self.setScene(self.p)
        self.show()

        def toQColor(color):
            return QColor(color[0] * 255, color[1] * 255, color[2] * 255, color[3] * 255)

        for type in [self.graph.nodes, self.graph.edges]:
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
        graph = Widget()
        self.setCentralWidget(graph)

        dock = QDockWidget("Content", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        edit = QTextEdit()
        dock.setWidget(edit)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

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
                edit.setText(" ".join(base.arguments))
                table.setRowCount(len(base.env))
                table.clearContents()

                row = 0
                for key, value in base.env.items():
                    table.setItem(row, 0, QTableWidgetItem(key))
                    table.setItem(row, 1, QTableWidgetItem(value))
                    row += 1
            elif isinstance(base, Edge) and base.file:
                edit.setText(open(base.file, 'rb').read().decode('utf-8', 'ignore'))

        graph.onSelected.connect(display)

        dock2 = QDockWidget("test", self)
        dock2.setWidget(QPushButton("Info", dock2))
        self.addDockWidget(Qt.RightDockWidgetArea, dock2)


def main():
    app = QtWidgets.QApplication([])
    window = ExampleApp()
    window.setWindowTitle('GUI')
    window.setFixedSize(1024, 768)
    window.show()
    app.exec_()


main()
