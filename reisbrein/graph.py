import collections


class Edge:
    def __init__(self, from_vertex, to_vertex, distance):
        self.from_vertex = from_vertex
        self.to_vertex = to_vertex
        self.distance = distance


class Graph:

    def __init__(self):
        self.vertices = set()

        # makes the default value for all vertices an empty list
        self.neighbors = collections.defaultdict(list)
        self.edges = {}
 
    def add_vertex(self, value):
        self.vertices.add(value)
 
    def add_edge(self, edge):
        if edge.from_vertex == edge.to_vertex:
            pass    # no cycles allowed
        self.neighbors[edge.from_vertex].append(edge.to_vertex)
        self.edges[(edge.from_vertex, edge.to_vertex)] = edge
 
    def __str__(self):
        string = "Vertices: " + str(self.vertices) + "\n"
        string += "Neighbors: " + str(self.neighbors) + "\n"
        string += "Edges: " + str(self.edges)
        return string

 
def dijkstra(graph, start):
    # initializations
    S = set()
 
    # delta represents the length shortest distance paths from start -> v, for v in delta. 
    # We initialize it so that every vertex has a path of infinity (this line will break if you run python 2)
    delta = dict.fromkeys(list(graph.vertices), float('inf'))
    previous = dict.fromkeys(list(graph.vertices), None)
 
    # then we set the path length of the start vertex to 0
    delta[start] = 0
 
    # while there exists a vertex v not in S
    while S != graph.vertices:
        # let v be the closest vertex that has not been visited...it will begin at 'start'
        v = min((set(delta.keys()) - S), key=delta.get)
 
        # for each neighbor of v not in S
        for neighbor in set(graph.neighbors[v]) - S:
            new_path = delta[v] + graph.edges[v, neighbor].distance
 
            # is the new path from neighbor through 
            if new_path < delta[neighbor]:
                # since it's optimal, update the shortest path for neighbor
                delta[neighbor] = new_path
 
                # set the previous vertex of neighbor to v
                previous[neighbor] = v
        S.add(v)

    return delta, previous
 
 
# Uses dijkstra function in order to output the shortest path from start to end
def shortest_path(graph, start, end):
    delta, previous = dijkstra(graph, start)
    
    path = []
    vertex = end
 
    while vertex is not None:
        path.append(vertex)
        vertex = previous[vertex]
 
    path.reverse()
    return path