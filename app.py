from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor, QPolygon
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtGui import QPainterPath
from PyQt5.QtWidgets import QLabel

from xdot import *


class MyParser(XDotParser):
    def handle_edge(self, src_id, dst_id, attrs):
        super().handle_edge(src_id, dst_id, attrs)


class Widget(QtWidgets.QWidget):
    def __init__(self, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        parser = MyParser(open("a.xdot").read().encode('utf-8'))
        self.graph = parser.parse()

    def paintEvent(self, QPaintEvent):
        super().paintEvent(QPaintEvent)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setWindow(0, 0, self.width(), self.height())
        p.setViewport(0, 0, self.width(), self.height())
        p.begin(self)
        p.setPen(QColor(168, 34, 3))
        p.setBrush(QColor(168, 34, 3))

        def toQColor(color):
            return QColor(color[0] * 255, color[1] * 255, color[2] * 255, color[3] * 255)

        for type in [self.graph.nodes, self.graph.edges]:
            for node in type:
                for shape in node.shapes:
                    if isinstance(shape, EllipseShape):
                        if shape.filled:
                            p.setBrush(toQColor(shape.pen.fillcolor))
                        else:
                            p.setBrush(QColor(0, 0, 0, 0))
                        p.drawEllipse(shape.x0 - shape.w / 2.0, shape.y0 - shape.h / 2.0, shape.w, shape.h)
                    elif isinstance(shape, TextShape):
                        p.setFont(QFont(shape.pen.fontname, shape.pen.fontsize))
                        p.drawText(shape.x, shape.y, shape.t)
                    elif isinstance(shape, BezierShape):
                        path = QPainterPath()
                        path.moveTo(shape.points[0][0], shape.points[0][1])

                        for part in shape.points:
                            path.lineTo(part[0], part[1])

                        p.setBrush(QColor(0,0,0,0))
                        p.drawPath(path)
                    elif isinstance(shape, PolygonShape):
                        polygon = QPolygon()
                        for point in shape.points:
                            polygon.append(QPoint(point[0], point[1]))
                        p.drawPolygon(polygon)
                    else:
                        print("unknown")


        #p.drawLine(1, 1, 100, 100)
        #p.drawLine(10, 1, 100, 100)
        #p.drawEllipse(10, 10, 10, 10)
        #p.drawEllipse(81, 41, 10, 10)
        p.end()


class ExampleApp(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(ExampleApp, self).__init__(parent)
        w = Widget(self)
        w.setGeometry(0, 0, self.width(), self.height())

def main():
    app = QtWidgets.QApplication([])
    window = ExampleApp()
    window.show()
    app.exec_()

main()
