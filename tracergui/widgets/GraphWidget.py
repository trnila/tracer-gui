from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView

from tracergui.nodes import Base, Process


class GraphWidget(QtWidgets.QGraphicsView):
    onSelected = pyqtSignal(object)
    showPid = pyqtSignal(int)

    def __init__(self, data):
        super().__init__()
        self.data = data

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setMouseTracking(True)

        self.p = QGraphicsScene(self)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing)

        self.setScene(self.p)

        self.showPid.connect(self.handle_show_pid)
        self.onSelected.connect(self.handle_select)

    def handle_show_pid(self, pid):
        for node in self.p.items():
            if isinstance(node, Process) and node.process.process['pid'] == pid:
                self.onSelected.emit(node)

    def handle_select(self, object):
        for i in self.p.selectedItems():
            i.setSelected(False)

        object.setSelected(True)

    def create_graph(self, filter=None):
        self.graph = self.data.create_graph(filter)
        self.p.clear()
        for type in [self.graph.shapes, self.graph.nodes, self.graph.edges]:
            for node in type:
                if isinstance(node, QGraphicsItem):
                    self.p.addItem(node)

    def apply_filter(self, query):
        self.create_graph(filter=query)

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
            self.onSelected.emit(item)
