import sys
from io import StringIO

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
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTextEdit

from DotWriter import DotWriter
from dot.parser import XDotParser
from nodes import Base, Process, Edge
from TracedData import TracedData


class Widget(QtWidgets.QGraphicsView):
    onSelected = pyqtSignal(Base)

    def __init__(self, data):
        super().__init__()

        str = StringIO()
        dot_writer = DotWriter(str)
        dot_writer.begin()

        for pid, process in data.data.items():
            dot_writer.write_node(pid, process['executable'])

            if process['parent'] > 0:
                dot_writer.write_edge(process['parent'], pid)

            def format(fd):
                if 'file' in fd:
                    return fd['file']

                if 'src' in fd:
                    return "%s:%d\\n<->\\n%s:%d" % (
                        fd['src']['address'], fd['src']['port'],
                        fd['dst']['address'], fd['dst']['port']
                    )

                if fd['type'] == 'pipe':
                    return 'pipe:[%s]' % fd['inode']

                return fd

            for id, name in process['read'].items():
                dot_writer.write_node(id, format(name))
                dot_writer.write_edge(id, pid)

            for id, name in process['write'].items():
                dot_writer.write_node(id, format(name))
                dot_writer.write_edge(pid, id)

        dot_writer.end()

        with open("/tmp/a.dot", "w") as f:
            f.write(str.getvalue())

        import os
        os.system("sh -c 'dot -Txdot /tmp/a.dot > /tmp/a.xdot'")

        parser = XDotParser(open("/tmp/a.xdot").read().encode('utf-8'), data)
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

        dir = sys.argv[1] if len(sys.argv) >= 2 else '/tmp/report'
        data = TracedData(dir)
        data.load()

        graph = Widget(data)
        self.setCentralWidget(graph)

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

        dock1.hide()
        dock2.hide()

        def display(base):
            dock1.hide()
            dock2.hide()

            if isinstance(base, Process):
                edit.setText(" ".join(base.arguments))
                table.setRowCount(len(base.env))
                table.clearContents()

                row = 0
                for key, value in base.env.items():
                    table.setItem(row, 0, QTableWidgetItem(key))
                    table.setItem(row, 1, QTableWidgetItem(value))
                    row += 1

                dock1.show()
                dock2.show()
            elif isinstance(base, Edge) and base.file:
                edit.setText(data.read_file(base.file['content']).decode('utf-8', 'ignore'))
                dock1.show()

        graph.onSelected.connect(display)

        # dock2 = QDockWidget("test", self)
        # dock2.setWidget(QPushButton("Info", dock2))
        # self.addDockWidget(Qt.RightDockWidgetArea, dock2)


def main():
    app = QtWidgets.QApplication([])
    window = ExampleApp()
    window.setWindowTitle('GUI')
    window.setFixedSize(1024, 768)
    window.show()
    app.exec_()


main()
