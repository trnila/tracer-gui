from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtGui import QPainterPath
from PyQt5.QtGui import QPolygonF
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from xdot import *


class MyParser(XDotParser):
	def handle_edge(self, src_id, dst_id, attrs):
		super().handle_edge(src_id, dst_id, attrs)


class Widget(QtWidgets.QGraphicsView):
	def __init__(self):
		super().__init__()

		parser = MyParser(open("a.xdot").read().encode('utf-8'))
		self.graph = parser.parse()

		self.p = p = QGraphicsScene(self)
		self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing)

		self.setScene(self.p)
		self.show()

		def toQColor(color):
			return QColor(color[0] * 255, color[1] * 255, color[2] * 255, color[3] * 255)

		for type in [self.graph.nodes, self.graph.edges]:
			for node in type:
				for shape in node.shapes:
					if isinstance(shape, EllipseShape):
						e = p.addEllipse(shape.x0 - shape.w / 2.0, shape.y0 - shape.h / 2.0, shape.w, shape.h)

						if shape.filled:
							e.setBrush(toQColor(shape.pen.fillcolor))
					elif isinstance(shape, TextShape):
						p.setFont(QFont(shape.pen.fontname, shape.pen.fontsize))
						text = p.addText(shape.t)
						text.setPos(shape.x, shape.y)
					elif isinstance(shape, BezierShape):
						path = QPainterPath()
						path.moveTo(shape.points[0][0], shape.points[0][1])

						for part in shape.points:
							path.lineTo(part[0], part[1])

						p.addPath(path)
					elif isinstance(shape, PolygonShape):
						polygon = QPolygonF()
						for point in shape.points:
							polygon.append(QPoint(point[0], point[1]))
						p.addPolygon(polygon, QColor(0, 0, 0))
					else:
						print("unknown")

						# self.fitInView(p.itemsBoundingRect(), Qt.Qt.KeepAspectRatio)

	def wheelEvent(self, evt):
		scale = 1.2 if evt.angleDelta().y() > 0 else 0.8

		self.scale(scale, scale)
		self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)


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
