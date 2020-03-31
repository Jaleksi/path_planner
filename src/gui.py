import os

from PyQt5 import QtWidgets, QtGui, QtCore

from .node_file import Node


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setWindowTitle('kauppa_router')
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)
        self.init_menus()

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
            self.canvas.new_route(img_path)
            self.resize(self.canvas.x() + self.canvas.image.width(),
                        self.canvas.y() + self.canvas.image.height())


class Canvas(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.image = None
        self.nodes = []
        self.mode = 'view'

    def change_mode(self, mode):
        assert mode in ['view', 'node_edit']
        if mode == 'node_edit':
            if not self.image:
                return
            self.mode = mode

    def new_route(self, img):
        self.image = QtGui.QPixmap(img)
        self.update()

    def paintEvent(self, event):
        if not self.image:
            return
        p = QtGui.QPainter(self)
        p.drawPixmap(self.rect(), self.image)

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self.mode == 'node_edit':
            p = QtGui.QPainter(self.image)
            self.drawPoint(event, p)
            self.update()

    def mouseMoveEvent(self, event):
        pass

    def drawPoint(self, event, p):
        pen = QtGui.QPen(QtCore.Qt.green)
        pen.setWidth(10)
        p.setPen(pen)
        self.nodes.append(Node(event.pos().x(), event.pos().y()))
        p.drawPoint(event.pos())
        print([(n.x, n.y) for n in self.nodes])
