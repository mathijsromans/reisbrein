import copy
from datetime import timedelta

from geopy.geocoders import Nominatim
from reisbrein.api.tomtom import TomTomApi
from reisbrein.api.mapquest import MapQuestApi
from .graph import Graph, shortest_path
from .segment import TransportType
from .userpreference import order_by_preference
from .models import UserTravelPreferences


def recur_map(f, data):
    return [not hasattr(x, "__iter__") and f(x) or recur_map(f, x) for x in data]


class Location:
    def __init__(self, loc_str, location=(0,0)):
        # geolocator = Nominatim()
        self.loc_str = loc_str
        self.location = location if location != (0,0) else TomTomApi().search(loc_str)
        # geolocator.geocode(self.loc_str)

    def gps(self):
        return self.location

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
    def __init__(self, generator, router):
        self.generator = generator
        self.router = router

    def solve(self, start_loc, end_loc, start_time, user_preferences=UserTravelPreferences()):
        start = Point(Location(start_loc), start_time)
        end = Point(Location(end_loc), start_time + timedelta(hours=12))
        edges = self.generator.create_edges(start, end)
        routes = self.router.make_routes(start, end, edges)
        for p in routes:
            if p and p[-1].transport_type == TransportType.WAIT:
                p.pop()
        # print(list(map(str, p)))
        order_by_preference(routes, user_preferences)
        return routes

    def routes(self, start, end, edges):
        raise NotImplementedError()


class RichRouter(object):

    def make_routes(self, start, end, edges):
        new_routes = [[edge] for edge in self.edges_starting_at(start, edges)]
        num_changes = 0
        final_routes = []
        while new_routes:
            partial_routes = []
            for p in new_routes:
                if p[-1].to_vertex == end:
                    final_routes.append(p)
                else:
                    partial_routes.append(p)
            num_changes += len(new_routes)
            if num_changes > 1000:
                break
            new_routes.clear()
            for p in partial_routes:
                for e in self.edges_starting_at(p[-1].to_vertex, edges):
                    new_p = copy.deepcopy(p)
                    new_p.append(e)
                    new_routes.append(new_p)
            # print(list(recur_map(str, partial_routes)))

        return final_routes

    @staticmethod
    def edges_starting_at(point, edges):
        return filter(lambda x: x.from_vertex == point, edges)


class DijkstraRouter(object):

    def make_routes(self, start, end, edges):
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