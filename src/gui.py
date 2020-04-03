# Standard
import os

# 3rd party
from PyQt5 import QtWidgets

# Local
from .widgets.canvas import Canvas
from .widgets.item_list import ItemList


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('kauppa_router')
        self.setGeometry(10, 10, 500, 500)
        self.init_menus()
        self.init_layout()

    def init_layout(self):
        '''
        Create layout for canvas and item list.
        main_widget is just filler-widget to apply layout.
        '''
        layout = QtWidgets.QHBoxLayout()
        self.main_widget = QtWidgets.QWidget()
        self.canvas = Canvas()
        self.item_list = ItemList()
        self.canvas.setMouseTracking(True)
        self.setCentralWidget(self.main_widget)
        layout.addWidget(self.canvas, 80)
        layout.addWidget(self.item_list, 20)
        self.main_widget.setLayout(layout)

    def init_menus(self):
        '''Create toolbar menus'''
        # Exit
        exit_action = QtWidgets.QAction('Exit', self)
        exit_action.triggered.connect(self.close)

        # Load image
        load_action = QtWidgets.QAction('Load image', self)
        load_action.triggered.connect(self.load_image)

        # Mode actions
        self.route_action = QtWidgets.QAction('Edit route', self)
        self.route_action.triggered.connect(lambda: self.set_mode('route_edit'))

        self.view_action = QtWidgets.QAction('View', self)
        self.view_action.triggered.connect(lambda: self.set_mode('view'))
        self.view_action.setEnabled(False)

        self.target_action = QtWidgets.QAction('Edit targets', self)
        self.target_action.triggered.connect(lambda: self.set_mode('target_edit'))

        mb = self.menuBar()
        filemenu = mb.addMenu('File')
        filemenu_items = [load_action, exit_action]
        for item in filemenu_items:
            filemenu.addAction(item)
        modemenu = mb.addMenu('Mode')
        modemenu_items = [self.view_action, self.route_action, self.target_action]
        for item in modemenu_items:
            modemenu.addAction(item)

    def set_mode(self, mode):
        assert mode in ['view', 'target_edit', 'route_edit'], f'{mode} not valid mode'
        if mode == 'route_edit':
            self.route_action.setEnabled(False)
            self.view_action.setEnabled(True)
            self.target_action.setEnabled(True)
        elif mode == 'view':
            self.route_action.setEnabled(True)
            self.view_action.setEnabled(False)
            self.target_action.setEnabled(True)
        elif mode == 'target_edit':
            self.route_action.setEnabled(True)
            self.view_action.setEnabled(True)
            self.target_action.setEnabled(False)

        self.canvas.change_mode(mode)

    def load_image(self):
        dialog = QtWidgets.QFileDialog(self)
        img_path, _ = dialog.getOpenFileName(self, "Load image", "")
        if os.path.exists(img_path):
            self.canvas.new_image(img_path)
            self.resize(self.canvas.x() + self.canvas.image.width(),
                        self.canvas.y() + self.canvas.image.height())
