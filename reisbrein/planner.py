from .graph import Graph, shortest_path, Edge
from.segment import Segment, TransportType


class Planner:
    def __init__(self):
        pass

    def solve(self, start, end):
        edges = self.create_test_edges()
        graphs = [
            self.create_graph(edges),
            self.create_graph(self.exclude(edges, TransportType.BIKE)),
            self.create_graph(self.exclude(edges, TransportType.TRAIN)),
        ]

        return [shortest_path(g, start, end) for g in graphs]

    @staticmethod
    def exclude(edges, transport_type):
        return [e for e in edges if e.transport_type != transport_type ]


    @staticmethod
    def create_test_edges():
        edges = [Segment(TransportType.BIKE, 'a', 'b', 20),
                 Segment(TransportType.TRAIN, 'a', 'c', 80),
                 Segment(TransportType.TRAIN, 'a', 'd', 50),
                 Segment(TransportType.TRAIN, 'b', 'c', 10),
                 Segment(TransportType.BIKE, 'c', 'e', 30),
                 Segment(TransportType.TRAIN, 'd', 'e', 40),
                 Segment(TransportType.CAR, 'a', 'e', 70)]
        return edges

    @staticmethod
    def create_graph(edges):

        vertices = set()
        for e in edges:
            vertices.add(e.from_vertex)
            vertices.add(e.to_vertex)

        G = Graph()

        for v in vertices:
            G.add_vertex(v)

        for e in edges:
            G.add_edge(e)

        return G