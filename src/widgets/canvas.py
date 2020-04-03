# 3rd party
from PyQt5 import QtWidgets, QtGui, QtCore

# Local
from ..node_file import RouteNode, TargetNode, closest_segment_point


class Canvas(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.image = None
        self.route_nodes = []
        self.mode = 'View'
        self.selected_node = None
        self.pairing_node = None
        self.pairs = []
        self.targets = []
        self.target_help_dot = None

    def change_mode(self, mode):
        if not self.image:
            return
        self.mode = mode

    def clear_selections(self):
        self.selected_node = None
        self.pairing_node.pairing = False
        self.pairing_node = None
        self.mode = 'node_edit'

    def new_image(self, img):
        self.image = QtGui.QPixmap(img)
        self.update()

    def add_route_node(self):
        mx, my = self.mousepos
        self.route_nodes.append(RouteNode(mx, my, (0, 0, 255)))

    def del_route_node(self):
        self.pairs = [pair for pair in self.pairs if self.selected_node not in pair]
        self.route_nodes.remove(self.selected_node)

    def new_pair(self):
        if self.pairing_node == self.selected_node:
            self.clear_selections()
            return
        for pair in self.pairs:
            if self.pairing_node in pair and self.selected_node in pair:
                self.clear_selections()
                return
        self.pairs.append((self.selected_node, self.pairing_node))
        self.pairing_node.pairing = False
        self.pairing_node = None
        self.mode = 'route_edit'

    def translate_original_to_resized(self, x, y):
        new_x = x * self.width() / self.image.width()
        new_y = y * self.height() / self.image.height()
        return (new_x, new_y)

    def translated_mousepos(self, x, y):
        trns_x = x / (self.width() / self.image.width())
        trns_y = y / (self.height() / self.image.height())
        return (int(trns_x), int(trns_y))

    def set_helper_dot_position(self):
        pos = closest_segment_point(self.mousepos, self.pairs)
        self.target_help_dot = self.translate_original_to_resized(pos[0], pos[1])

    def paintEvent(self, event):
        if not self.image:
            return

        p = QtGui.QPainter(self)
        p.drawPixmap(self.rect(), self.image)
        pen = QtGui.QPen()
        pen.setWidth(10)

        for node in self.route_nodes:
            r, g, b = node.color
            pen.setColor(QtGui.QColor(r, g, b))
            p.setPen(pen)
            x, y = self.translate_original_to_resized(node.x, node.y)
            p.drawPoint(x, y)

        for p1, p2 in self.pairs:
            pen.setWidth(3)
            pen.setColor(QtGui.QColor(255, 0, 255))
            p.setPen(pen)
            p1_x, p1_y = self.translate_original_to_resized(p1.x, p1.y)
            p2_x, p2_y = self.translate_original_to_resized(p2.x, p2.y)
            p.drawLine(p1_x, p1_y, p2_x, p2_y)

        if self.mode == 'target_edit' and self.target_help_dot is not None:
            pen.setWidth(15)
            pen.setColor(QtGui.QColor(0, 255, 0))
            p.setPen(pen)
            p.drawPoint(self.target_help_dot[0], self.target_help_dot[1])

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.mode == 'route_edit' and self.selected_node is None:
                self.add_route_node()
            elif self.mode == 'pairing' and self.selected_node is not None:
                self.new_pair()
        elif event.buttons() == QtCore.Qt.RightButton:
            if self.mode == 'route_edit' and self.selected_node is not None:
                self.del_route_node()
        self.update()

    def mouseDoubleClickEvent(self, event):
        if not self.selected_node:
            return
        self.pairing_node = self.selected_node
        self.pairing_node.pairing = True
        self.mode = 'pairing'

    def mouseMoveEvent(self, event):
        if self.image is None:
            return
        self.mousepos = self.translated_mousepos(event.pos().x(), event.pos().y())
        left_mb = event.buttons() == QtCore.Qt.LeftButton

        # Moving node
        if left_mb and self.selected_node and self.mode == 'route_edit':
            self.selected_node.x, self.selected_node.y = self.mousepos

        # Mouse over canvas
        if not left_mb and self.mode in ['route_edit', 'pairing']:
            self.selected_node = None
            for node in self.route_nodes:
                if self.selected_node is None and node.within_reach(self.mousepos):
                    self.selected_node = node
                    node.color = (255, 0, 0)
                elif node.pairing:
                    node.color = (0, 255, 0)
                else:
                    node.color = (0, 0, 255)

        elif self.mode == 'target_edit':
            self.set_helper_dot_position()

        self.update()
