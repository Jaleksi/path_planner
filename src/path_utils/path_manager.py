# Standard
from math import factorial
from itertools import permutations

# Local
from ..node_file import points_distance
from .dijkstra import dijkstra
from .tsp import tsp

class PathManager:
    def __init__(self, progress_bar, nodes, targets, start, end):
        self.pb = progress_bar
        self.nodes = nodes
        self.start_node = start
        self.end_node = end
        self.target_nodes = [n.parent_node for n in targets]
        self.distances = self.get_unique_connections()

    def activate_progressbar(self, msg, maximum):
        '''Set message and max value for progress bar'''
        self.pb.setWindowTitle(msg)
        self.pb.setMaximum(maximum)
        self.pb.setMinimum(0)
        self.pb.forceShow()

    def get_shortest_route(self, mode):
        '''
        dijkstra: Go through all possible routes/permutations of targets and return
        shortest
        tsp: Treat path as travelling salesman -problem, not as accurate
        '''
        if mode == 'dijkstra':
            return self.absolute_shortest_path()
        elif mode == 'tsp':
            return self.shortest_by_tsp()

    # Absolute shortest route methods
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

    def absolute_shortest_path(self):
        '''
        Gets shortest route between start node and end node while going through all
        the target nodes. Creates all possible permutations of the targets and
        returns the shortest path.
        '''
        self.activate_progressbar('Calculating all possible paths..',
                                  factorial(len(self.target_nodes)))
        permutation_count = 0

        shortest_distance = float('inf')
        shortest_route = None

        for perm in permutations(self.target_nodes):
            if self.pb.wasCanceled():
                return 0, []
            permutation_count += 1
            self.pb.setValue(permutation_count)

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

    # Travelling salesman methods
    def shortest_by_tsp(self):
        distances, paths, node_indexes = self.target_nodes_distances()
        # Add 3 because start-/end-node + dummy are not included in targets
        num_of_nodes = len(self.target_nodes) + 3
        tsp_path = list(tsp(distances=distances, num_of_nodes=num_of_nodes))
        start_index = self.get_start_node_index(node_indexes)
        while tsp_path[0] != start_index:
            tsp_path.insert(0, tsp_path.pop())
        node_path = self.indexlist_to_path(node_indexes, paths, tsp_path)
        return 0, node_path

    def target_nodes_distances(self):
        '''
        Get distances between targets with dijkstra.
        [(index_of_fist_node, index_of_second_node, distance_by_path)...]
        '''
        nodes = self.target_nodes.copy()
        nodes.extend([self.start_node, self.end_node])
        node_indexes = {
            0: 'dummy'
        }
        target_distances = []
        target_paths = []

        # Make sure distance is never the same
        deny_equal = 0.0000001
        for i, n1 in enumerate(nodes):
            node_indexes[i+1] = n1
            # Add dummy distance/path to set start and end point
            dist = deny_equal if n1 in [self.start_node, self.end_node] else 10000 + deny_equal
            target_distances.append((i+1, 0, dist))
            target_paths.append((n1, 'dummy', ()))
            deny_equal += deny_equal
            for j, n2 in enumerate(nodes[i+1:]):
                dist, path = dijkstra(self.distances, n1, n2)
                target_distances.append((i+1, i+j+2, dist))
                target_paths.append((n1, n2, path))
        
        return target_distances, target_paths, node_indexes

    def indexlist_to_path(self, node_indexes, paths, tsp_path):
        '''Make node-to-node path (list) from tsp-path, which is a list of indexes'''
        shortest_path = []
        for i, node_index in enumerate(tsp_path[:-1]):
            node = node_indexes[node_index]
            next_node = node_indexes[tsp_path[i+1]]
            path_between_nodes = self.get_path_between_nodes(node, next_node, paths)
            shortest_path.extend(path_between_nodes)
        shortest_path.append(self.end_node)
        return shortest_path


    def get_path_between_nodes(self, n1, n2, paths):
        '''Find path between nodes which was calculated earlier in target_nodes_distances()'''
        for route in paths:
            connection = (route[0], route[1])
            if connection == (n1, n2):
                return list(route[2][:-1])
            elif connection == (n2, n1):
                return list(route[2][::-1][:-1])
        return None

    def get_start_node_index(self, index_list):
        for index, node in index_list.items():
            if node == self.start_node:
                return index
        return None
