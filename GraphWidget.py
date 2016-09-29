from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView

from nodes import Base


class GraphWidget(QtWidgets.QGraphicsView):
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

    def mousePressEvent(self, QMouseEvent):
        super().mousePressEvent(QMouseEvent)
        item = self.itemAt(QMouseEvent.x(), QMouseEvent.y())

        while item and not isinstance(item, Base):
            item = item.parentItem()

        if item:
            print(item)
            self.onSelected.emit(item)
