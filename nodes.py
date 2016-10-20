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

    def setLabel(self, text):
        self.addToGroup(text)
        self.label = text

    def setPen(self, color):
        for i in self.childItems():
            i.setPen(color)

    def shape(self):
        for i in self.childItems():
            if isinstance(i, MyPath):
                return i.shape()

        return super().shape()


class MyPath(QGraphicsPathItem):
    # clip only path
    def shape(self):
        qp = QPainterPathStroker()
        qp.setWidth(10)
        qp.setCapStyle(Qt.SquareCap)
        return qp.createStroke(self.path())


class Edge(Base):
    def __init__(self, src, dst, points):
        super().__init__()
        self.file = None
        self.src = src
        self.dst = dst

        path = QPainterPath()
        path.moveTo(points[0][0], points[0][1])

        for part in points:
            path.lineTo(part[0], part[1])

        p = MyPath(path)
        p.setAcceptHoverEvents(True)
        self.addToGroup(p)

    def add(self, points):
        self.addToGroup(points)

    def __repr__(self):
        return "%s -> %s" % (self.src, self.dst)

class Ellipse(Base):
    def __init__(self, *__args):
        super().__init__()

        ellipse = QGraphicsEllipseItem(*__args)
        self.addToGroup(ellipse)
        ellipse.setAcceptHoverEvents(True)

class Polygon(Base):
    def __init__(self, points, filled = False):
        super().__init__()

        polygon = QPolygonF()

        for point in points:
            polygon.append(QPoint(point[0], point[1]))
        p = QGraphicsPolygonItem(polygon)
        self.addToGroup(p)

class Text(QGraphicsTextItem):
    def __init__(self, str, x, y, size, w, fontname):
        super().__init__()
        font = QFont(fontname)

        fontMetrics = QFontMetrics(font)
        scale = float(fontMetrics.width(str)) / w
        font.setPointSizeF(font.pointSizeF() / scale)

        self.setFont(font)
        self.setPos(x - w / 2, y - fontMetrics.height())
        self.setPlainText(str)

class Process(Ellipse):
    def __init__(self, process, *__args):
        super().__init__(*__args)
        self.process = process
        self.neighbours = []
        self.action = process

    def __repr__(self):
        return self.process.process['executable']


class Resource(Ellipse):
    def __init__(self, resource, *__args):
        super().__init__(*__args)
        self.resource = resource
        self.neighbours = []
