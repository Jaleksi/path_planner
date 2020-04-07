from collections import defaultdict
from itertools import permutations
import heapq

from ..node_file import points_distance


class PathManager:
    def __init__(self, nodes, targets, start, end):
        self.nodes = nodes
        self.start_node = start
        print(self.start_node)
        self.end_node = end
        self.target_nodes = [n.parent_node for n in targets]
        self.distances = self.get_unique_connections()

    def get_unique_connections(self):
        '''conncetions = [(node_object, node_object, distance)...]'''
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
            connections.append(con + (int(distance), ))
        return connections

    def get_shortest_route(self):
        shortest_distance = float('inf')
        shortest_route = None
        #for perm in permutations(self.target_nodes):
        #    dist, route = self.full_path_length(list(perm))
        #    if dist > shortest_distance:
        #        continue
        #    shortest_distance, shortest_route = dist, route
        shortest_distance, shortest_route = self.full_path_length(list(self.target_nodes))
        return shortest_distance, shortest_route

    def full_path_length(self, permutation):
        total_distance = 0
        route = []
        permutation.insert(0, self.start_node)
        permutation.append(self.end_node)
        # Calculate target paths in permutation
        for i, node in enumerate(permutation[:-1]):
            dist, path = dijkstra(self.distances, node, permutation[i+1])
            total_distance += dist
            route.extend(path)
        return total_distance, route

    def dj(self):
        return dijkstra(self.distances, self.start_node, self.end_node)

def dijkstra(edges, f, t):
    '''https://gist.github.com/kachayev/5990802'''

    g = defaultdict(set)
    for l, r, c in edges:
        g[l].add((c, r))
        g[r].add((c, l))

    q, seen, mins = [(0, f, ())], set(), {f: 0}
    while q:
        (cost, v1, path) = heapq.heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, )
            if v1 == t:
                return cost, path

            for c, v2 in g.get(v1, ()):
                if v2 in seen:
                    continue
                prev = mins.get(v2, None)
                next = cost + c
                if prev is None or next < prev:
                    mins[v2] = next
                    heapq.heappush(q, (next, v2, path))
    return float("inf")
