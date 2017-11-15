from datetime import timedelta
from geopy.geocoders import Nominatim
from .graph import Graph, shortest_path
from .segment import TransportType


class Location:
    def __init__(self, loc_str):
        geolocator = Nominatim()
        self.loc_str = loc_str
        self.location = geolocator.geocode(self.loc_str)

    def gps(self):
        return (self.location.latitude, self.location.longitude) if self.location else None

    def __str__(self):
        return self.loc_str

    @property
    def latitude(self):
        return self.location.latitude

    @property
    def longitude(self):
        return self.location.longitude


class Point:
    def __init__(self, location, time):
        self.location = location
        self.time = time

    def __str__(self):
        return str(self.location) + ' @ ' + str(self.time)


class Planner(object):
    def __init__(self, generator):
        self.generator = generator

    def solve(self, start_loc, end_loc, start_time):
        start = Point(Location(start_loc), start_time)
        end = Point(Location(end_loc), start_time + timedelta(hours=12))
        edges = self.generator.create_edges(start, end)
        return self.make_plans(start, end, edges)

    def make_plans(self, start, end, edges):
        raise NotImplementedError()


class DijkstraPlanner(Planner):

    def make_plans(self, start, end, edges):
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