import math


class Node:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.pairs = []
        self.color = color

    def within_reach(self, x, y):
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2) < 10
