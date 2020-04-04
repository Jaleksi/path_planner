# Standard
import math

# 3rd party
from PyQt5.QtWidgets import QListWidgetItem

class RouteNode:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.pairs = []
        self.color = color
        self.pairing = False

    def within_reach(self, mpos):
        return points_distance((self.x, self.y), mpos) <= 8


class TargetNode(QListWidgetItem):
    def __init__(self, num, text, mx, my, actual_x, actual_y):
        super().__init__()
        self.num = num
        self.text = text
        self.x = actual_x
        self.y = actual_y
        self.draw_x = mx
        self.draw_y = my
        self.setText(f'[{self.num}] {self.text}')


def closest_segment_point(point, route_pairs):
    closest_point = None
    dist_to_closest = math.inf

    for segment in route_pairs:
        point_a, point_b = segment[0], segment[1]
        dx = point_b.x - point_a.x
        dy = point_b.y - point_a.y
        dr2 = float(dx ** 2 + dy ** 2)

        lerp = ((point[0] - point_a.x) * dx + (point[1] - point_a.y) * dy) / dr2

        if lerp <= 0:
            lerp = 0
        elif lerp >= 1:
            lerp = 1

        x = lerp * dx + point_a.x
        y = lerp * dy + point_a.y

        dist = points_distance((x, y), point)
        if dist < dist_to_closest:
            dist_to_closest = dist
            closest_point = (int(x), int(y))

    return closest_point


def points_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
