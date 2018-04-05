import copy
import logging
import time
from collections import defaultdict
from datetime import timedelta
from reisbrein.generator.generator import Generator
from reisbrein.generator.gen_common import FixTime
from .graph import Graph, shortest_path
from .primitives import Point, TransportType
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
        for segment in route:
            self.travel_time += segment.time_sec

    def is_round_trip(self):
        return not self.route or self.route[0].from_vertex.location == self.route[-1].to_vertex.location

    class VehicleIncosistency(Exception):
        pass

    ''' a used vehicle cannot be used from a different location where it was left '''
    def get_vehicle_movements(self):
        vehicles_from_to = {}  # { vehicle_1 : {'from': from_loc, 'to': to_loc), ... }
        for segment in self.route:
            vehicle = segment.unique_vehicle
            if vehicle:
                if vehicle in vehicles_from_to:
                    if segment.from_vertex.location != vehicles_from_to[vehicle]['to']:
                        # a used vehicle cannot be used from a different location where it was left
                        raise self.VehicleIncosistency()
                    vehicles_from_to[vehicle]['to'] = segment.to_vertex.location
                else:
                    vehicles_from_to[vehicle] = {'from': segment.from_vertex.location, 'to': segment.to_vertex.location}
        return vehicles_from_to

    def is_legal_partial_plan(self):
        try:
            self.get_vehicle_movements()
        except self.VehicleIncosistency:
            return False
        return True

    def is_legal_final_plan(self):
        try:
            vehicles_from_to = self.get_vehicle_movements()
        except self.VehicleIncosistency:
            return False
        if self.is_round_trip():
            for veh, from_to in vehicles_from_to.items():
                if from_to['from'] != from_to['to']:
                    # a vehicle must be returned to where it came from
                    return False
        return True

    def departure_time(self):
        for s in self.route:
            if s.transport_type != TransportType.WAIT:
                return s.from_vertex.time

    def __str__(self):
        return str(list(map(str, self.route)))


class RichRouter(object):

    def make_plans(self, start, end, edges):
        from_to_edge_dict = defaultdict(list)
        for e in edges:
            # logger.info(str(e) + str(id(e.from_vertex.location)) + '-' + str(id(e.to_vertex.location)))
            from_to_edge_dict[e.from_vertex].append(e)
        new_plans = [Plan([edge]) for edge in from_to_edge_dict[start]]
        num_changes = 0
        final_plans = []
        while new_plans:
            logger.info('There are ' + str(len(new_plans)) + ' new_plans, ' + str(len(final_plans)) + ' final_plans')
            num_changes += len(new_plans)
            if num_changes > 100000:
                logger.error('num_changes search limit exceeded')
                break
            if len(final_plans) > 1000:
                logger.error('final_plans search limit exceeded')
                break
            partial_plans = []
            for p in new_plans:
                if p.route[-1].to_vertex == end:
                    if p.is_legal_final_plan():
                        final_plans.append(p)
                else:
                    for e in from_to_edge_dict[p.route[-1].to_vertex]:
                        new_p = Plan(copy.copy(p.route))
                        new_p.route.append(e)
                        if new_p.is_legal_partial_plan():
                            partial_plans.append(new_p)
            new_plans = partial_plans
        logger.info('Made ' + str(len(final_plans)) + ' plans')
        return final_plans


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
        if not plans:
            return
        if plans[0].is_round_trip():
            logger.info('is round trip')
            earliest_departure = min(p.departure_time() for p in plans)
            logger.info('earliest_departure = ' + str(earliest_departure))
            for p in plans:
                s1 = p.route[0]
                s2 = p.route[-1]
                if s1.transport_type == TransportType.WAIT:
                    if s1.to_vertex.time == earliest_departure:
                        p.route.pop(0)
                    else:
                        s1.from_vertex.time = earliest_departure
                        s1.transport_type = TransportType.INVISIBLE_WAIT
                if s2.transport_type == TransportType.WAIT:
                    p.route.pop(-1)
        else:
            for p in plans:
                if fix_time == FixTime.END and p.route[0].transport_type == TransportType.WAIT:
                    p.route.pop(0)
                if fix_time == FixTime.START and p.route[-1].transport_type == TransportType.WAIT:
                    p.route.pop(-1)

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
        # for e in edges:
        #     logger.info('Edge: ' + str(e))
        plans = self.router.make_plans(start, end, edges)
        plans = list(filter(self.has_no_double_biking, plans))
        order_and_select(plans, user_preferences, fix_time)
        self.remove_unnecessary_waiting(plans, fix_time)
        log_end = time.time()
        logger.info('END - time: ' + str(log_end - log_start))
        return plans
