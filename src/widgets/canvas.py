# 3rd party
from PyQt5 import QtWidgets, QtGui, QtCore

# Local
from ..node_file import RouteNode, TargetNode, closest_segment_point


class Canvas(QtWidgets.QLabel):
    new_target_signal = QtCore.pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.image = None
        self.route_nodes = []
        self.mode = 'view'
        self.selected_node = None
        self.pairing_node = None
        self.pairs = []
        self.target_nodes = []
        self.target_actual_pos = None

    # Canvas-related methods
    def change_mode(self, mode):
        self.mode = mode
        if mode == 'target_edit':
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        else:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)

        if mode == 'view':
            print([((p1.x, p1.y), (p2.x, p2.y)) for p1, p2 in self.pairs])
            print([(n.parent_node.x, n.parent_node.y) for n in self.target_nodes])

    def allow_mode_change(self):
        return self.image is not None

    def clear_selections(self):
        self.selected_node = None
        self.pairing_node.pairing = False
        self.pairing_node = None
        self.mode = 'node_edit'

    def set_pen_style(self, pen, style):
        color = {
            'route_line': (0, 0, 255),
            'target_help': (0, 255, 0),
            'target_node_draw': (255, 128, 0),
            'target_line': (255, 128, 0),
            'text': (0, 0, 0)
            }
        width = {
            'route_line': 3,
            'target_help': 15,
            'target_node_draw': 10,
            'target_line': 3,
            'text': 5
            }

        r, g, b = color[style]
        pen.setColor(QtGui.QColor(r, g, b))
        pen.setWidth(width[style])
        return pen
                
    def new_image(self, img):
        self.image = QtGui.QPixmap(img)
        self.update()
    
    def translate_original_to_resized(self, x, y):
        new_x = x * self.width() / self.image.width()
        new_y = y * self.height() / self.image.height()
        return (new_x, new_y)

    def translated_mousepos(self, x, y):
        trns_x = x / (self.width() / self.image.width())
        trns_y = y / (self.height() / self.image.height())
        return (int(trns_x), int(trns_y))

    # Route-related methods
    def add_route_node(self, pos=None):
        mx, my = self.mousepos if pos is None else pos
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

    def push_node_between_pairs(self, pair):
        self.pairs.remove(pair)
        node = self.route_nodes[-1]
        for p in pair:
            self.pairs.append((p, node))

    
    # Target-related methods
    def add_target_node(self):
        txt, done = QtWidgets.QInputDialog.getText(self, 'New target', 'Target name:')
        if not done or txt == '':
            return
        mx, my = self.mousepos
        pos, pair = closest_segment_point(self.mousepos, self.pairs)

        num = len(self.target_nodes) + 1
        self.add_route_node(pos)
        self.push_node_between_pairs(pair)
        new_target = TargetNode(num, txt, mx, my, self.route_nodes[-1])
        self.target_nodes.append(new_target)
        self.new_target_signal.emit(new_target)

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
        if self.pairs:
            p.setPen(self.set_pen_style(pen, 'route_line'))
            for p1, p2 in self.pairs:
                p1_x, p1_y = self.translate_original_to_resized(p1.x, p1.y)
                p2_x, p2_y = self.translate_original_to_resized(p2.x, p2.y)
                p.drawLine(p1_x, p1_y, p2_x, p2_y)
        
        if self.route_nodes:
            pen.setWidth(10)
            for node in self.route_nodes:
                r, g, b = node.color
                pen.setColor(QtGui.QColor(r, g, b))
                p.setPen(pen)
                x, y = self.translate_original_to_resized(node.x, node.y)
                p.drawPoint(x, y)

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.mode == 'route_edit' and self.selected_node is None:
                self.add_route_node()
            elif self.mode == 'pairing' and self.selected_node is not None:
                self.new_pair()
            elif self.mode == 'target_edit':
                self.add_target_node()
            
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

        self.update()
