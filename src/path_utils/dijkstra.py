# Standard
from collections import defaultdict
import heapq


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
