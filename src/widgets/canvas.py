# 3rd party
from PyQt5 import QtWidgets, QtGui, QtCore

# Local
from ..node_file import Node


class Canvas(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.image = None
        self.nodes = []
        self.mode = 'view'
        self.selected_node = None
        self.pairing_node = None
        self.pairs = []

    def change_mode(self, mode):
        if mode == 'node_edit':
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

    def add_node(self):
        mx, my = self.mousepos
        self.nodes.append(Node(mx, my, (0, 0, 255)))

    def del_node(self):
        self.pairs = [pair for pair in self.pairs if self.selected_node not in pair]
        self.nodes.remove(self.selected_node)

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
        self.mode = 'node_edit'

    def translate_original_to_resized(self, node):
        x = node.x * self.width() / self.image.width()
        y = node.y * self.height() / self.image.height()
        return (x, y)

    def translated_mousepos(self, x, y):
        trns_x = x / (self.width() / self.image.width())
        trns_y = y / (self.height() / self.image.height())
        return (int(trns_x), int(trns_y))

    def paintEvent(self, event):
        if not self.image:
            return

        p = QtGui.QPainter(self)
        p.drawPixmap(self.rect(), self.image)
        pen = QtGui.QPen()
        pen.setWidth(10)

        for node in self.nodes:
            r, g, b = node.color
            pen.setColor(QtGui.QColor(r, g, b))
            p.setPen(pen)
            x, y = self.translate_original_to_resized(node)
            p.drawPoint(x, y)

        for p1, p2 in self.pairs:
            pen.setWidth(3)
            pen.setColor(QtGui.QColor(255, 0, 255))
            p.setPen(pen)
            p1_x, p1_y = self.translate_original_to_resized(p1)
            p2_x, p2_y = self.translate_original_to_resized(p2)
            p.drawLine(p1_x, p1_y, p2_x, p2_y)

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.mode == 'node_edit' and self.selected_node is None:
                self.add_node()
            if self.mode == 'pairing' and self.selected_node is not None:
                self.new_pair()
        elif event.buttons() == QtCore.Qt.RightButton:
            if self.mode == 'node_edit' and self.selected_node is not None:
                self.del_node()
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
        if left_mb and self.selected_node and self.mode == 'node_edit':
            self.selected_node.x, self.selected_node.y = self.mousepos

        # Mouse over canvas
        if not left_mb:
            self.selected_node = None
            for node in self.nodes:
                if self.selected_node is None and node.within_reach(self.mousepos):
                    self.selected_node = node
                    node.color = (255, 0, 0)
                elif node.pairing:
                    node.color = (0, 255, 0)
                else:
                    node.color = (0, 0, 255)
        self.update()
