# Standard
from math import factorial
from collections import defaultdict
from itertools import permutations
import heapq

# 3rd party
from PyQt5.QtWidgets import QProgressDialog
from PyQt5 import QtCore

# Local
from ..node_file import points_distance


class PathManager:
    def __init__(self, parent, nodes, targets, start, end):
        self.canvas = parent
        self.nodes = nodes
        self.start_node = start
        self.end_node = end
        self.target_nodes = [n.parent_node for n in targets]
        self.distances = self.get_unique_connections()

    def get_unique_connections(self):
        '''
        Creates a list which contains all connections between nodes and the distance.
        Stripts duplicate connections like (A, B), (B, A).
        connections = [(node_object, node_object, distance), ...]
        '''
        pairs = []
        for node in self.nodes:
            assert node.connects_with, 'Found node without connections, exiting.'
            for connection in node.connects_with:
                # Continue if connection already in list from other node
                if (node, connection)[::-1] in pairs:
                    continue
                pairs.append((node, connection))

        # Add distances
        connections = []
        for con in pairs:
            p1, p2 = con[0], con[1]
            distance = points_distance((p1.x, p1.y), (p2.x, p2.y))
            connections.append(con + (distance, ))
        return connections

    def get_shortest_route(self):
        '''
        Gets shortest route between start node and end node while going through all
        the target nodes. Creates all possible permutations of the targets and
        returns the shortest path.
        '''
        # Setup progress-bar
        progress_bar = QProgressDialog(self.canvas)
        progress_bar.setWindowTitle('Calculating all possible paths..')
        progress_bar.setMaximum(factorial(len(self.target_nodes)))
        progress_bar.setMinimum(0)
        progress_bar.setWindowModality(QtCore.Qt.WindowModal)
        progress_bar.forceShow()
        permutation_count = 0

        shortest_distance = float('inf')
        shortest_route = None

        for perm in permutations(self.target_nodes):
            if progress_bar.wasCanceled():
                return 0, []
            permutation_count += 1
            progress_bar.setValue(permutation_count)

            dist, route = self.full_path_length(list(perm))
            if dist > shortest_distance:
                continue
            shortest_distance, shortest_route = dist, route
        return shortest_distance, shortest_route

    def full_path_length(self, permutation):
        '''
        Calculates the distance between start- and end-node while going through the
        target nodes for given permutation of targets.
        '''
        total_distance = 0
        route = []

        # Add start and end nodes to permutation
        permutation.insert(0, self.start_node)
        permutation.append(self.end_node)

        # Calculate target paths in permutation
        for i, node in enumerate(permutation[:-1]):
            dist, path = dijkstra(self.distances, node, permutation[i+1])
            total_distance += dist
            # Remove last because it is in next paths first (remove duplicate)
            route.extend(path[:-1])

        route.append(self.end_node)
        return total_distance, route


def dijkstra(edges, f, t):
    '''
    TAKEN FROM: https://gist.github.com/kachayev/5990802

    Calculate the shortest route between given 2 nodes.
    '''

    g = defaultdict(set)
    for l, r, c in edges:
        g[l].add((c, r))
        g[r].add((c, l))

    q, seen, mins = [(0, f, ())], set(), {f: 0}
    while q:
        (cost, v1, path) = heapq.heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path += (v1, )
            if v1 == t:
                return cost, path

            for c, v2 in g.get(v1, ()):
                if v2 in seen:
                    continue
                prev = mins.get(v2, None)
                next_ = cost + c
                if prev is None or next_ < prev:
                    mins[v2] = next_
                    heapq.heappush(q, (next_, v2, path))
    return float("inf")
