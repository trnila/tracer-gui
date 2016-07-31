from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from dot.parser import XDotParser


class Widget(QtWidgets.QGraphicsView):
    def __init__(self):
        super().__init__()

        parser = XDotParser(open("a.xdot").read().encode('utf-8'))
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


class ExampleApp(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)

        frame = QWidget()
        layout = QVBoxLayout(frame)
        frame.show()

        layout.addWidget(Widget())

        self.setCentralWidget(frame)


def main():
    app = QtWidgets.QApplication([])
    window = ExampleApp()
    window.setWindowTitle('GUI')
    window.setFixedSize(800, 600)
    window.show()
    app.exec_()


main()
