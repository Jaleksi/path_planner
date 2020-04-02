import math


class Node:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.pairs = []
        self.color = color
        self.pairing = False

    def within_reach(self, mpos):
        return math.sqrt((self.x - mpos[0]) ** 2 + (self.y - mpos[1]) ** 2) <= 8
