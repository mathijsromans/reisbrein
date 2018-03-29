import copy
import logging
import time
from datetime import timedelta
from reisbrein.generator.generator import Generator
from reisbrein.generator.gen_common import FixTime
from .graph import Graph, shortest_path
from .primitives import Point, Location, TransportType
from .userpreference import order_and_select
from .models import UserTravelPreferences

logger = logging.getLogger(__name__)


def recur_map(f, data):
    return [not hasattr(x, "__iter__") and f(x) or recur_map(f, x) for x in data]


class Plan():
    def __init__(self, route):
        self.route = route
        self.score = 0
        self.travel_time = 0
        self.vehicle_left = None
        for segment in route:
            self.travel_time += segment.time_sec

    def __str__(self):
        return str(list(map(str, self.route)))


class RichRouter(object):

    def make_plans(self, start, end, edges):
        new_plans = [Plan([edge]) for edge in self.edges_starting_at(start, edges)]
        num_changes = 0
        final_plans = []
        while new_plans:
            num_changes += len(new_plans)
            if num_changes > 1000:
                logger.error('make_plans search limit exceeded')
                break
            partial_plans = []
            for p in new_plans:
                if p.route[-1].to_vertex == end:
                    final_plans.append(p)
                else:
                    partial_plans.append(p)
            new_plans.clear()
            for p in partial_plans:
                for e in self.edges_starting_at(p.route[-1].to_vertex, edges):
                    new_p = copy.copy(p)
                    new_p.route.append(e)
                    new_plans.append(new_p)
            # print(list(recur_map(str, partial_routes)))

        return final_plans

    @staticmethod
    def edges_starting_at(point, edges):
        return filter(lambda x: x.from_vertex == point, edges)


class DijkstraRouter(object):

    def make_plans(self, start, end, edges):
        graphs = [
            self.create_graph(edges),
            self.create_graph(self.exclude(edges, TransportType.BIKE)),
            self.create_graph(self.exclude(edges, TransportType.TRAIN)),
        ]

        return [Plan(shortest_path(g, start, end)) for g in graphs]

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


class Planner():
    def __init__(self, generator=Generator, router=RichRouter):
        self.generator = generator()
        self.router = router()

    @staticmethod
    def has_no_double_biking(plan):
        for index, segment in enumerate(plan.route[:-1]):
            if plan.route[index].transport_type == TransportType.BIKE and \
               plan.route[index+1].transport_type == TransportType.BIKE:
                return False
        return True

    @staticmethod
    def remove_unnecessary_waiting(plans, fix_time):
        for p in plans:
            if p.route:
                n = 0 if fix_time == FixTime.END else len(p.route)-1  # remove waiting at the time which is NOT fixed
            if p.route[n].transport_type == TransportType.WAIT:
                p.route.pop(n)

    def solve(self, start_loc, end_loc, req_time, fix_time, user_preferences=UserTravelPreferences()):
        logger.info('BEGIN')
        log_start = time.time()
        if fix_time == FixTime.START:
            start_time = req_time
            end_time = req_time + timedelta(hours=12)
        else:
            start_time = req_time - timedelta(hours=12)
            end_time = req_time
        start = Point(start_loc, start_time)
        end = Point(end_loc, end_time)
        edges = self.generator.create_edges(start, end, fix_time)
        plans = self.router.make_plans(start, end, edges)
        plans = list(filter(self.has_no_double_biking, plans))
        self.remove_unnecessary_waiting(plans, fix_time)
        order_and_select(plans, user_preferences)
        log_end = time.time()
        logger.info('END - time: ' + str(log_end - log_start))
        return plans
