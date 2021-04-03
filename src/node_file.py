# Standard
import math
import json
import os

# 3rd party
from PyQt5.QtWidgets import QListWidgetItem


class RouteNode:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.connects_with = []
        self.color = color
        self.pairing = False
        self.reach_radius = 10

    def within_reach(self, mpos):
        return points_distance((self.x, self.y), mpos) <= self.reach_radius


class TargetNode(QListWidgetItem):
    def __init__(self, num, text, mx, my, parent_node):
        super().__init__()
        self.num = num
        self.text = text
        self.draw_x = mx
        self.draw_y = my
        self.parent_node = parent_node
        self.update_text()

    def update_text(self):
        self.setText(f'[{self.num}] {self.text}')


def closest_segment_point(point, route_pairs):
    '''https://stackoverflow.com/questions/27161533/find-the-shortest-distance-between-a-point-and-line-segments-not-line

    This function is used to draw line between target's actual position on the route
    and graphic that shows target number (where user clicked).
    '''
    closest_point = None
    dist_to_closest = math.inf
    pair = None

    for segment in route_pairs:
        node_a, node_b = segment[0], segment[1]
        dx = node_b.x - node_a.x
        dy = node_b.y - node_a.y
        dr2 = float(dx ** 2 + dy ** 2) + 0.0000001

        lerp = ((point[0] - node_a.x) * dx + (point[1] - node_a.y) * dy) / dr2

        if lerp <= 0:
            lerp = 0
        elif lerp >= 1:
            lerp = 1

        x = lerp * dx + node_a.x
        y = lerp * dy + node_a.y

        dist = points_distance((x, y), point)
        if dist < dist_to_closest:
            dist_to_closest = dist
            closest_point = (int(x), int(y))
            pair = segment

    return closest_point, pair


def points_distance(p1, p2):
    '''Returns distance between two points'''
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def save_nodes_to_file(file_path, route_nodes):
    node_dict = {}
    for i, node in enumerate(route_nodes):
        node_connections = [route_nodes.index(c) for c in node.connects_with]
        node_dict[i] = {
            'coords': (node.x, node.y),
            'connects_with': node_connections
        }

    json_path = f'{os.path.splitext(file_path)[0]}.json'
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(node_dict, json_file, indent=2)

def load_nodes_from_file(path_to_json):
    if not path_to_json.lower().endswith('.json'):
        return

    with open(path_to_json, 'r') as node_json:
        node_dict = json.load(node_json)

    # Create node-objects
    node_objects = []
    for i, node in node_dict.items():
        x, y = node['coords']
        new_node = RouteNode(x, y, (0, 0, 255))
        node_objects.append(new_node)

    # Add connections
    for i, node_obj in enumerate(node_objects):
        c_indexes = node_dict[str(i)]['connects_with']
        node_obj.connects_with.extend([node_objects[i] for i in c_indexes])
    
    return node_objects
