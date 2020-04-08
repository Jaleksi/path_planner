# Standard
import math

# 3rd party
from PyQt5.QtWidgets import QListWidgetItem


class RouteNode:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.connects_with = []
        self.color = color
        self.pairing = False

    def within_reach(self, mpos):
        return points_distance((self.x, self.y), mpos) <= 10


class TargetNode(QListWidgetItem):
    def __init__(self, num, text, mx, my, parent_node):
        super().__init__()
        self.num = num
        self.text = text
        self.draw_x = mx
        self.draw_y = my
        self.parent_node = parent_node
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
        dr2 = float(dx ** 2 + dy ** 2)

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
