import copy
from datetime import timedelta
from reisbrein.generator.generator import Generator
from .graph import Graph, shortest_path
from .primitives import Point, Location, TransportType
from .userpreference import order_and_select
from .models import UserTravelPreferences


def recur_map(f, data):
    return [not hasattr(x, "__iter__") and f(x) or recur_map(f, x) for x in data]


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


class Plan():
    def __init__(self, route):
        self.route = route
        self.score = 0
        self.travel_time = 0
        for segment in route:
            self.travel_time += segment.time_sec

    def __str__(self):
        return str(list(map(str, self.route)))


class Planner():
    def __init__(self, generator=Generator, router=RichRouter):
        self.generator = generator()
        self.router = router()

    @staticmethod
    def has_no_double_biking(route):
        for index, segment in enumerate(route[:-1]):
            if route[index].transport_type == TransportType.BIKE and \
               route[index+1].transport_type == TransportType.BIKE:
                return False
        return True

    @staticmethod
    def remove_waiting_at_end(routes):
        for r in routes:
            if r and r[-1].transport_type == TransportType.WAIT:
                r.pop()

    def solve(self, start_loc, end_loc, start_time, user_preferences=UserTravelPreferences()):
        start = Point(Location(start_loc), start_time)
        end = Point(Location(end_loc), start_time + timedelta(hours=12))
        edges = self.generator.create_edges(start, end)
        routes = self.router.make_routes(start, end, edges)
        routes = list(filter(self.has_no_double_biking, routes))
        self.remove_waiting_at_end(routes)
        plans = [Plan(r) for r in routes]
        order_and_select(plans, user_preferences)
        return plans
