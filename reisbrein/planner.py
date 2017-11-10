from .graph import Graph, shortest_path, Edge


class Planner:
    def __init__(self):
        self.graph = self.get_test_graph()

    def solve(self, start, end):
        return shortest_path(self.graph, start, end)

    @staticmethod
    def get_test_graph():
        G = Graph()
        G.add_vertex('a')
        G.add_vertex('b')
        G.add_vertex('c')
        G.add_vertex('d')
        G.add_vertex('e')

        G.add_edge(Edge('a', 'b', 2))
        G.add_edge(Edge('a', 'c', 8))
        G.add_edge(Edge('a', 'd', 5))
        G.add_edge(Edge('b', 'c', 1))
        G.add_edge(Edge('c', 'e', 3))
        G.add_edge(Edge('d', 'e', 4))

        return G