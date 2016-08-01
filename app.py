from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTextEdit

from dot.parser import XDotParser
from nodes import Base, Process, Edge


class Widget(QtWidgets.QGraphicsView):
    onSelected = pyqtSignal(Base)

    def __init__(self):
        super().__init__()

        parser = XDotParser(open("/tmp/graph/graph.xdot").read().encode('utf-8'))
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

        def display(base):
            if isinstance(base, Process):
                edit.setText(open('/tmp/graph/' + base.arguments).read())
            elif isinstance(base, Edge) and base.file:
                edit.setText(open('/tmp/graph/' + base.file, 'rb').read().decode('utf-8', 'ignore'))

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
