# Standard
import os

# 3rd party
from PyQt5 import QtWidgets, QtGui, QtCore

# Local
from .node_file import Node


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('kauppa_router')
        self.canvas = Canvas()
        self.canvas.setMouseTracking(True)
        self.setCentralWidget(self.canvas)
        self.init_menus()
        self.setGeometry(10, 10, 500, 500)

    def init_menus(self):
        '''Create toolbar menus'''
        # Exit
        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.triggered.connect(self.close)

        # Load image
        load_action = QtWidgets.QAction('Load image', self)
        load_action.triggered.connect(self.load_image)

        # Insert nodes
        node_action = QtWidgets.QAction('Edit nodes', self)
        node_action.triggered.connect(lambda: self.canvas.change_mode('node_edit'))

        mb = self.menuBar()
        filemenu = mb.addMenu('File')
        filemenu_items = [exit_action, load_action, node_action]
        for item in filemenu_items:
            filemenu.addAction(item)

    def load_image(self):
        dialog = QtWidgets.QFileDialog(self)
        img_path, _ = dialog.getOpenFileName(self, "Load image", "")
        if os.path.exists(img_path):
            self.canvas.new_image(img_path)
            self.resize(self.canvas.x() + self.canvas.image.width(),
                        self.canvas.y() + self.canvas.image.height())


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
            p.drawPoint(node.x, node.y)

        for p1, p2 in self.pairs:
            pen.setWidth(3)
            pen.setColor(QtGui.QColor(255, 0, 255))
            p.setPen(pen)
            p.drawLine(p1.x, p1.y, p2.x, p2.y)

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
        self.mousepos = (event.pos().x(), event.pos().y())
        left_mb = event.buttons() == QtCore.Qt.LeftButton

        # Moving node
        if left_mb and self.selected_node and self.mode == 'node_edit':
            self.selected_node.x, self.selected_node.y = self.mousepos

        # Mouse over canvas
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
