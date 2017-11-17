import copy
from datetime import timedelta

from geopy.geocoders import Nominatim

from .graph import Graph, shortest_path
from .segment import TransportType
from .userpreference import order_by_preference
from .models import UserTravelPreferences


def recur_map(f, data):
    return [not hasattr(x, "__iter__") and f(x) or recur_map(f, x) for x in data]


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

    def solve(self, start_loc, end_loc, start_time, user_preferences=UserTravelPreferences()):
        start = Point(Location(start_loc), start_time)
        end = Point(Location(end_loc), start_time + timedelta(hours=12))
        edges = self.generator.create_edges(start, end)
        plans = self.make_plans(start, end, edges)
        for p in plans:
            if p and p[-1].transport_type == TransportType.WAIT:
                p.pop()
        order_by_preference(plans)
        return plans

    def make_plans(self, start, end, edges):
        raise NotImplementedError()


class RichPlanner(Planner):

    def make_plans(self, start, end, edges):
        new_plans = [[edge] for edge in self.edges_starting_at(start, edges)]
        num_changes = 0
        final_plans = []
        while new_plans:
            partial_plans = []
            for p in new_plans:
                if p[-1].to_vertex == end:
                    final_plans.append(p)
                else:
                    partial_plans.append(p)
            num_changes += len(new_plans)
            if num_changes > 100:
                break
            new_plans.clear()
            for p in partial_plans:
                for e in self.edges_starting_at(p[-1].to_vertex, edges):
                    new_p = copy.deepcopy(p)
                    new_p.append(e)
                    new_plans.append(new_p)

        return final_plans

    @staticmethod
    def edges_starting_at(point, edges):
        return filter(lambda x: x.from_vertex == point, edges)


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