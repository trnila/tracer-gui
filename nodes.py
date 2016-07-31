from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFontMetrics
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPainterPath
from PyQt5.QtGui import QPainterPathStroker
from PyQt5.QtGui import QPolygonF
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtWidgets import QGraphicsItemGroup
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtWidgets import QGraphicsPolygonItem
from PyQt5.QtWidgets import QGraphicsTextItem


class Base(QGraphicsItemGroup):
    def hoverEnterEvent(self, QGraphicsSceneHoverEvent):
        super().hoverEnterEvent(QGraphicsSceneHoverEvent)

        for g in self.childItems():
            self.setColorTo(g, QColor(255, 0, 0))

    def hoverLeaveEvent(self, QGraphicsSceneHoverEvent):
        super().hoverLeaveEvent(QGraphicsSceneHoverEvent)

        for g in self.childItems():
            self.setColorTo(g, QColor(0, 0, 0))

    def setColorTo(self, g, color):
        if isinstance(g, QGraphicsTextItem):
            g.setDefaultTextColor(color)
        else:
            g.setPen(color)

    def setLabel(self, str, x, y, size, w, fontname):
        font = QFont(fontname)

        fontMetrics = QFontMetrics(font)
        scale = float(fontMetrics.width(str)) / w
        font.setPointSizeF(font.pointSizeF() / scale)

        item = QGraphicsTextItem(str)
        item.setFont(font)
        item.setPos(x - w / 2, y - fontMetrics.height())
        self.addToGroup(item)


class MyPath(QGraphicsPathItem):
    # clip only path
    def shape(self):
        qp = QPainterPathStroker()
        qp.setWidth(10)
        qp.setCapStyle(Qt.SquareCap)
        return qp.createStroke(self.path())


class Edge(Base):
    def __init__(self, points):
        super().__init__()

        path = QPainterPath()
        path.moveTo(points[0][0], points[0][1])

        for part in points:
            path.lineTo(part[0], part[1])

        p = MyPath(path)
        p.setAcceptHoverEvents(True)
        self.addToGroup(p)

    def add(self, points):
        polygon = QPolygonF()

        for point in points.points:
            polygon.append(QPoint(point[0], point[1]))
            p = QGraphicsPolygonItem(polygon)
            self.addToGroup(p)


class Ellipse(Base):
    def __init__(self, *__args):
        super().__init__()

        ellipse = QGraphicsEllipseItem(*__args)
        self.addToGroup(ellipse)
        ellipse.setAcceptHoverEvents(True)