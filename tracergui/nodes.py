from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFontMetrics
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPainterPath
from PyQt5.QtGui import QPainterPathStroker
from PyQt5.QtGui import QPolygonF
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsItemGroup
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtWidgets import QGraphicsPolygonItem
from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtWidgets import QStyle


class Base(QGraphicsItemGroup):
    SECOND_FOCUS = 0

    def __init__(self):
        super().__init__()
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.hovered = False

    def calc_color(self):
        if self.hasSecondFocus():
            return QColor(0, 0, 255)

        if self.hovered:
            return QColor(255, 0, 0)

        if self.isSelected():
            return QColor(255, 0, 0)

        return QColor(0, 0, 0)

    def itemChange(self, evt, val):
        if evt == QGraphicsItem.ItemSelectedChange and not val:
            for g in self.childItems():
                if not g.isSelected():
                    self.setColorTo(g, QColor(0, 0, 0))

        return super().itemChange(evt, val)

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        for g in self.childItems():
            self.setColorTo(g, self.calc_color())

        QStyleOptionGraphicsItem.state &= ~QStyle.State_Selected
        return super().paint(QPainter, QStyleOptionGraphicsItem, widget)

    def hoverEnterEvent(self, QGraphicsSceneHoverEvent):
        super().hoverEnterEvent(QGraphicsSceneHoverEvent)
        self.hovered = True

        for g in self.childItems():
            g.hovered = True
            self.setColorTo(g, self.calc_color())

    def hoverLeaveEvent(self, QGraphicsSceneHoverEvent):
        super().hoverLeaveEvent(QGraphicsSceneHoverEvent)
        self.hovered = False

        for g in self.childItems():
            g.hovered = False
            self.setColorTo(g, self.calc_color())

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

    def setSecondFocus(self, focus):
        self.setData(self.SECOND_FOCUS, focus)

        for ch in self.childItems():
            ch.setData(self.SECOND_FOCUS, focus)

    def hasSecondFocus(self):
        return self.data(self.SECOND_FOCUS)

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

        for i in range(1, len(points), 3):
            path.cubicTo(
                points[i][0], points[i][1],
                points[i + 1][0], points[i + 1][1],
                points[i + 2][0], points[i + 2][1]
            )

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
    def __init__(self, points, filled=False):
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


class Process(Base):
    def __init__(self, process, *__args):
        super().__init__()

        rect = QGraphicsRectItem(*__args)
        self.addToGroup(rect)
        rect.setAcceptHoverEvents(True)

        self.process = process
        self.neighbours = []
        self.action = process

        if process.process['thread']:
            rect.setBrush(QColor(255, 250, 205))

    def __repr__(self):
        return self.process.process['executable']


class Resource(Ellipse):
    def __init__(self, resource, *__args):
        super().__init__(*__args)
        self.resource = resource
        self.neighbours = []
