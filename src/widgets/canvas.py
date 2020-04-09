# 3rd party
from PyQt5 import QtWidgets, QtGui, QtCore

# Local
from ..node_file import RouteNode, TargetNode, closest_segment_point
from ..path_utils.path_manager import PathManager


class Canvas(QtWidgets.QLabel):
    info_signal = QtCore.pyqtSignal(str)
    new_target_signal = QtCore.pyqtSignal(object)
    del_target_signal = QtCore.pyqtSignal(object)
    toggle_menu_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.image = None
        self.route_nodes = []
        self.start_node = None
        self.end_node = None
        self.mode = 'route_edit'
        self.shortest_path = []
        self.selected_node = None
        self.pairing_node = None
        self.target_nodes = []
        self.target_actual_pos = None

    # Canvas-related methods
    def change_mode(self, mode):
        if mode != 'view' and self.shortest_path:
            self.shortest_path = []
        self.mode = mode

    def allow_mode_change(self):
        return self.image is not None

    def clear_selections(self):
        self.selected_node = None
        self.pairing_node.pairing = False
        self.pairing_node = None
        self.mode = 'route_edit'
        self.toggle_menu_signal.emit('route_edit')

    def set_pen_style(self, pen, style):
        color = {
            'route_line': (0, 0, 255),
            'route_line_shortest': (0, 255, 128),
            'target_help': (0, 255, 0),
            'target_node_draw': (255, 128, 0),
            'target_line': (255, 128, 0),
            'text': (0, 0, 0)
            }
        width = {
            'route_line': 3,
            'route_line_shortest': 10,
            'target_help': 15,
            'target_node_draw': 10,
            'target_line': 3,
            'text': 5
            }

        r, g, b = color[style]
        pen.setColor(QtGui.QColor(r, g, b))
        pen.setWidth(width[style])
        return pen

    def get_node_color(self, node):
        node_colors = {
            'normal': (0, 0, 255),
            'pairing': (0, 255, 0),
            'start': (0, 100, 50),
            'end': (255, 0, 127),
            'selected': (255, 0, 0)
        }
        if node == self.selected_node:
            return node_colors['selected']
        elif node == self.start_node:
            return node_colors['start']
        elif node == self.end_node:
            return node_colors['end']
        elif node == self.pairing_node:
            return node_colors['pairing']
        return node_colors['normal']

    def new_image(self, img):
        self.image = QtGui.QPixmap(img)
        self.toggle_menu_signal.emit('allow_path_calculate')
        self.update()

    def translate_original_to_resized(self, x, y):
        new_x = x * self.width() / self.image.width()
        new_y = y * self.height() / self.image.height()
        return (new_x, new_y)

    def translated_mousepos(self, x, y):
        trns_x = x / (self.width() / self.image.width())
        trns_y = y / (self.height() / self.image.height())
        return (int(trns_x), int(trns_y))

    def calculate_path(self):
        if self.start_node is None:
            self.info_signal.emit('Start node is not set!')
            return
        elif self.end_node is None:
            self.info_signal.emit('End node is not set!')
            return
        elif not self.target_nodes:
            self.info_signal.emit('Zero targets set!')
            return
        elif any([True for n in self.route_nodes if not n.connects_with]):
            self.info_signal.emit('All nodes are not connected!')
            return

        progress_bar = QtWidgets.QProgressDialog(self)
        progress_bar.setWindowModality(QtCore.Qt.WindowModal)
        path_manager = PathManager(progress_bar, self.route_nodes, self.target_nodes,
                                   self.start_node, self.end_node)
        distance, path = path_manager.get_shortest_route()
        if not path:
            return
        self.shortest_path = path
        self.mode = 'view'
        self.toggle_menu_signal.emit('view')
        self.update()

    # Route-related methods
    def set_start_node(self):
        self.start_node = self.selected_node
        self.update()

    def set_end_node(self):
        if self.end_node is not None:
            self.end_node.color = (0, 0, 255)
        self.selected_node.color = (255, 0, 127)
        self.end_node = self.selected_node
        self.update()

    def add_route_node(self, pos=None):
        mx, my = self.mousepos if pos is None else pos
        self.route_nodes.append(RouteNode(mx, my, (0, 0, 255)))

    def del_route_node(self):
        for node in self.route_nodes:
            cleaned_list = [n for n in node.connects_with if n != self.selected_node]
            node.connects_with = cleaned_list
        self.route_nodes.remove(self.selected_node)
        for target in self.target_nodes:
            if target.parent_node != self.selected_node:
                continue
            self.remove_target(target)
        self.update()

    def new_connection(self):
        pn, sn = self.pairing_node, self.selected_node
        if pn == sn:
            self.clear_selections()
            return
        if sn in pn.connects_with or pn in sn.connects_with:
            return

        sn.connects_with.append(pn)
        pn.connects_with.append(sn)

        self.pairing_node.pairing = False
        self.pairing_node = None
        self.mode = 'route_edit'
        self.toggle_menu_signal.emit('route_edit')

    def push_node_between_pairs(self, pair):
        n1, n2 = pair
        n1.connects_with.remove(n2)
        n2.connects_with.remove(n1)

        new_node = self.route_nodes[-1]
        for node in n1, n2:
            node.connects_with.append(new_node)
            new_node.connects_with.append(node)

    def get_route_lines(self):
        lines = []
        if self.shortest_path and self.mode == 'view':
            for n1, n2 in zip(self.shortest_path[:-1], self.shortest_path[1:]):
                lines.append((n1, n2))
        else:
            for node in self.route_nodes:
                # Continue if node doesn't have any connections
                if not node.connects_with:
                    continue
                for connection in node.connects_with:
                    # Continue if connection already in list from other node
                    if (node, connection)[::-1] in lines:
                        continue
                    lines.append((node, connection))
        return lines

    # Target-related methods
    def add_target_node(self):
        txt, done = QtWidgets.QInputDialog.getText(self, 'New target', 'Target name:')
        if not done or txt == '':
            return
        mx, my = self.mousepos
        pos, pair = closest_segment_point(self.mousepos, self.get_route_lines())

        num = len(self.target_nodes) + 1
        self.add_route_node(pos)
        self.push_node_between_pairs(pair)
        new_target = TargetNode(num, txt, mx, my, self.route_nodes[-1])
        self.target_nodes.append(new_target)
        self.new_target_signal.emit(new_target)

    def remove_target(self, target):
        self.target_nodes.remove(target)
        self.del_target_signal.emit(target)
        self.update_list_numbers()

    def update_list_numbers(self):
        for i, item in enumerate(self.target_nodes):
            item.num = i+1
            item.setText(f'[{item.num}] {item.text}')

    # Events
    def paintEvent(self, event):
        if not self.image:
            return

        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.drawPixmap(self.rect(), self.image)
        pen = QtGui.QPen()
        p.setFont(QtGui.QFont('Decorative', 10))
        # Draw target
        if self.target_nodes:
            for node in self.target_nodes:
                drx, dry = self.translate_original_to_resized(node.draw_x, node.draw_y)
                x, y = self.translate_original_to_resized(node.parent_node.x,
                                                          node.parent_node.y)
                p.setPen(self.set_pen_style(pen, 'target_line'))
                p.drawLine(drx, dry, x, y)

                p.setPen(self.set_pen_style(pen, 'target_node_draw'))
                p.drawEllipse(drx-3, dry-3, 6, 6)
                p.setPen(self.set_pen_style(pen, 'text'))
                p.drawText(drx-3, dry+3, str(node.num))

        # Draw route
        route_lines = self.get_route_lines()
        if route_lines:
            style = 'route_line_shortest' if self.shortest_path else 'route_line'
            p.setPen(self.set_pen_style(pen, style))
            for p1, p2 in route_lines:
                p1_x, p1_y = self.translate_original_to_resized(p1.x, p1.y)
                p2_x, p2_y = self.translate_original_to_resized(p2.x, p2.y)
                p.drawLine(p1_x, p1_y, p2_x, p2_y)

        if self.route_nodes and self.mode != 'view':
            pen.setWidth(10)
            for node in self.route_nodes:
                r, g, b = self.get_node_color(node)
                pen.setColor(QtGui.QColor(r, g, b))
                p.setPen(pen)
                x, y = self.translate_original_to_resized(node.x, node.y)
                p.drawPoint(x, y)

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.mode == 'route_edit' and self.selected_node is None:
                self.add_route_node()
            elif self.mode == 'pairing' and self.selected_node is not None:
                self.new_connection()
            elif self.mode == 'target_edit':
                self.add_target_node()
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

        self.update()

    def contextMenuEvent(self, event):
        if self.selected_node is None:
            return
        menu = QtWidgets.QMenu(self)
        del_action = menu.addAction('Delete')
        set_start = menu.addAction('Set as start')
        set_end = menu.addAction('Set as end')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == del_action:
            self.del_route_node()
        elif action == set_start:
            self.set_start_node()
        elif action == set_end:
            self.set_end_node()
