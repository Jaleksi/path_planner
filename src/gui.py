# Standard
import os

# 3rd party
from PyQt5 import QtWidgets

# Local
from .widgets.canvas import Canvas
from .widgets.item_list import ItemList
from .node_file import save_nodes_to_file, load_nodes_from_file


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_name = None
        self.setWindowTitle('route_finder')
        self.setGeometry(100, 100, 500, 500)
        self.init_layout()
        self.init_menus()
        self.canvas.new_target_signal.connect(self.add_target_to_list)
        self.canvas.del_target_signal.connect(self.remove_target_from_list)
        self.canvas.info_signal.connect(self.display_message)
        self.canvas.toggle_menu_signal.connect(self.toggle_menu_buttons)

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

        # Load nodes
        self.node_load_action = QtWidgets.QAction('Load nodes', self)
        self.node_load_action.triggered.connect(self.load_from_file)
        self.node_load_action.setEnabled(False)

        # Save nodes
        self.save_action = QtWidgets.QAction('Save nodes', self)
        self.save_action.triggered.connect(self.save_to_file)
        self.save_action.setEnabled(False)

        # Clear all
        clear_action = QtWidgets.QAction('Clear all nodes', self)
        clear_action.triggered.connect(self.canvas.clear_all_nodes)

        # Calculate path
        dijkstra_action = QtWidgets.QAction('Absolute shortest', self)
        dijkstra_action.triggered.connect(lambda: self.calculate_path('dijkstra'))

        tsp_action = QtWidgets.QAction('Approximate', self)
        tsp_action.triggered.connect(lambda: self.calculate_path('tsp'))

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
        for item in [load_action, self.save_action, self.node_load_action,
                     clear_action, exit_action]:
            filemenu.addAction(item)

        modemenu = mb.addMenu('Mode')
        for item in [self.view_action, self.route_action, self.target_action]:
            modemenu.addAction(item)

        self.path_menu = mb.addMenu('Calculate path')
        self.path_menu.setEnabled(False)
        for item in [dijkstra_action, tsp_action]:
            self.path_menu.addAction(item)

    def set_mode(self, mode):
        if not self.canvas.allow_mode_change():
            return
        self.toggle_menu_buttons(mode)
        self.canvas.change_mode(mode)

    def toggle_menu_buttons(self, mode):
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
        elif mode == 'allow_path_calculate':
            self.path_menu.setEnabled(True)

    def load_image(self):
        dialog = QtWidgets.QFileDialog(self)
        img_path, _ = dialog.getOpenFileName(self, "Load image", "")
        if not os.path.exists(img_path):
            return

        supported_image_formats = ['.jpg', '.png']
        given_image_ext = os.path.splitext(img_path)[1].lower()
        if given_image_ext not in supported_image_formats:
            self.display_message(f'{given_image_ext} not a valid format')
            return

        self.save_action.setEnabled(True)
        self.node_load_action.setEnabled(True)
        self.img_file = img_path
        self.canvas.new_image(img_path)
        img_x = self.canvas.image.width()
        img_y = self.canvas.image.height()
        self.resize(self.canvas.x() + img_x, self.canvas.y() + img_y)
        
        saved_node_file = f'{os.path.splitext(img_path)[0]}.json'
        if os.path.exists(saved_node_file):
            self.load_from_file(saved_node_file)

    def add_target_to_list(self, obj):
        self.item_list.new_target(obj)

    def remove_target_from_list(self, obj):
        self.item_list.del_target(obj)

    def display_message(self, msg):
        mb = QtWidgets.QMessageBox()
        mb.setIcon(QtWidgets.QMessageBox.Information)
        mb.setWindowTitle('Info')
        mb.setText(msg)
        mb.setStandardButtons(QtWidgets.QMessageBox.Ok)
        mb.exec_()

    def calculate_path(self, algo):
        self.canvas.calculate_path(algo)
        found_path = self.canvas.shortest_path
        if found_path:
            self.item_list.arrange_items(found_path)

    def save_to_file(self):
        route_nodes = self.canvas.route_nodes
        save_nodes_to_file(self.img_file, route_nodes)
        self.display_message(f'Nodes saved!')

    def load_from_file(self, json_path=None):
        if not json_path:
            dialog = QtWidgets.QFileDialog(self)
            json_path, _ = dialog.getOpenFileName(self, "Load nodes", "")
            if not os.path.exists(json_path):
                return
        try:
            loaded_nodes = load_nodes_from_file(json_path)
            self.canvas.clear_all_nodes()
            self.canvas.route_nodes = loaded_nodes
        except Exception as err:
            self.display_message(f'Could not load nodes: {err}')
