# Copyright 2008-2015 Jose Fonseca
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

class Shape:
	"""Abstract base class for all the drawing shapes."""

	def __init__(self):
		pass


class TextShape(Shape):
	LEFT, CENTER, RIGHT = -1, 0, 1

	def __init__(self, pen, x, y, j, w, t):
		Shape.__init__(self)
		self.pen = pen.copy()
		self.x = x
		self.y = y
		self.j = j  # Centering
		self.w = w  # width
		self.t = t  # text


class ImageShape(Shape):
	def __init__(self, pen, x0, y0, w, h, path):
		Shape.__init__(self)
		self.pen = pen.copy()
		self.x0 = x0
		self.y0 = y0
		self.w = w
		self.h = h
		self.path = path


class EllipseShape(Shape):
	def __init__(self, pen, x0, y0, w, h, filled=False):
		Shape.__init__(self)
		self.pen = pen.copy()
		self.x0 = x0
		self.y0 = y0
		self.w = w
		self.h = h
		self.filled = filled


class PolygonShape(Shape):
	def __init__(self, pen, points, filled=False):
		Shape.__init__(self)
		self.pen = pen.copy()
		self.points = points
		self.filled = filled


class LineShape(Shape):
	def __init__(self, pen, points):
		Shape.__init__(self)
		self.pen = pen.copy()
		self.points = points


class BezierShape(Shape):
	def __init__(self, pen, points, filled=False):
		Shape.__init__(self)
		self.pen = pen.copy()
		self.points = points
		self.filled = filled


class CompoundShape(Shape):
	def __init__(self, shapes):
		Shape.__init__(self)
		self.shapes = shapes


class Url(object):
	def __init__(self, item, url, highlight=None):
		self.item = item
		self.url = url
		if highlight is None:
			highlight = set([item])
		self.highlight = highlight


class Jump(object):
	def __init__(self, item, x, y, highlight=None):
		self.item = item
		self.x = x
		self.y = y
		if highlight is None:
			highlight = set([item])
		self.highlight = highlight


class Element(CompoundShape):
	"""Base class for graph nodes and edges."""

	def __init__(self, shapes):
		CompoundShape.__init__(self, shapes)

	def is_inside(self, x, y):
		return False

	def get_url(self, x, y):
		return None

	def get_jump(self, x, y):
		return None


class Node(Element):
	def __init__(self, id, x, y, w, h, shapes, url):
		Element.__init__(self, shapes)

		self.id = id
		self.x = x
		self.y = y

		self.x1 = x - 0.5 * w
		self.y1 = y - 0.5 * h
		self.x2 = x + 0.5 * w
		self.y2 = y + 0.5 * h

		self.url = url


def square_distance(x1, y1, x2, y2):
	deltax = x2 - x1
	deltay = y2 - y1
	return deltax * deltax + deltay * deltay


class Edge(Element):
	def __init__(self, src, dst, points, shapes):
		Element.__init__(self, shapes)
		self.src = src
		self.dst = dst
		self.points = points

	RADIUS = 10

	def is_inside_begin(self, x, y):
		return square_distance(x, y, *self.points[0]) <= self.RADIUS * self.RADIUS

	def is_inside_end(self, x, y):
		return square_distance(x, y, *self.points[-1]) <= self.RADIUS * self.RADIUS

	def is_inside(self, x, y):
		if self.is_inside_begin(x, y):
			return True
		if self.is_inside_end(x, y):
			return True
		return False

	def get_jump(self, x, y):
		if self.is_inside_begin(x, y):
			return Jump(self, self.dst.x, self.dst.y, highlight=set([self, self.dst]))
		if self.is_inside_end(x, y):
			return Jump(self, self.src.x, self.src.y, highlight=set([self, self.src]))
		return None

	def __repr__(self):
		return "<Edge %s -> %s>" % (self.src, self.dst)


class Graph:
	def __init__(self, nodes, edges):
		self.nodes = nodes
		self.edges = edges
