import collections
import logging
import time
from collections import defaultdict
from datetime import timedelta
from reisbrein.generator.generator import Generator
from reisbrein.generator.gen_common import FixTime
from .graph import Graph, shortest_path
from .primitives import Point, TransportType, Vehicle, VehicleType
from .userpreference import order_and_select
from .models import UserTravelPreferences
from reisbrein.api.ovfiets import OvFietsStations

logger = logging.getLogger(__name__)


def recur_map(f, data):
    return [not hasattr(x, "__iter__") and f(x) or recur_map(f, x) for x in data]


class VehiclePositions:
    def __init__(self):
        self.data = collections.defaultdict(set)  # { location : {vehicle1, vehicle2}, ... }

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return 'Vehicle positions: <' + str(self.data) + '>'

    def copy(self):
        new = VehiclePositions()

        # a shallow copy is not enough, a deepcopy is too much...
        for location in self.data:
            new.data[location] = self.data[location].copy()

        return new

    def add_vehicle(self, location, vehicle):
        self.data[location].add(vehicle)

    def apply_segment(self, segment):
        if not segment.transport_type.needs_vehicle():
            return None
        vehicles = self.data[segment.from_vertex.location]
        try:
            vehicle = next(v for v in vehicles if v.transport_type == segment.transport_type)
        except StopIteration as error:
            raise ValueError from error
        vehicles.remove(vehicle)
        if not vehicles:
            self.data.pop(segment.from_vertex.location)  # attention! needed for a proper __eq__ comparison
        self.data[segment.to_vertex.location].add(vehicle)
        return vehicle


class Plan():
    def __init__(self, init_vehicle_positions):
        assert isinstance(init_vehicle_positions, VehiclePositions)
        self.vehicle_positions = init_vehicle_positions.copy()
        self.segments = []
        self.segment_vehicles = {}  # { segment1: vehicle1, ... }
        self.score = 0
        self.travel_time = 0

    @property
    def route(self):
        return self.segments

    def copy(self):
        new = Plan(self.vehicle_positions)
        new.segments = self.segments.copy()
        new.segment_vehicles = self.segment_vehicles.copy()
        new.score = self.score
        new.travel_time = self.travel_time
        return new

    def add_segment(self, segment):
        if self.segments and segment.from_vertex != self.segments[-1].to_vertex:
            return False
        try:
            vehicle = self.vehicle_positions.apply_segment(segment)
        except ValueError:
            return False
        self.segments.append(segment)
        if vehicle:
            self.segment_vehicles[segment] = vehicle
        self.travel_time += segment.time_sec
        return True

    def is_round_trip(self):
        return not self.segments or self.segments[0].from_vertex.location == self.segments[-1].to_vertex.location

    class VehicleInconsistency(Exception):
        pass

    def is_legal_final_plan(self, init_vehicle_positions):
        # for a round trip, a vehicle must be returned to where it came from
        return not self.is_round_trip() or self.vehicle_positions == init_vehicle_positions

    def departure_time(self):
        for s in self.segments:
            if s.transport_type != TransportType.WAIT:
                return s.from_vertex.time

    def __str__(self):
        return '********* Plan ' + str(self.vehicle_positions) + ' ** ' + str(self.segment_vehicles) + ' ** ' + str(recur_map(str, self.segments))


class RichRouter(object):

    @staticmethod
    def make_plans(start, end, segments, init_vehicle_positions):
        print('Making plans from ' + str(start) + ' to ' + str(end))
        from_to_segments_dict = defaultdict(list)  # { location : [segment1, segment2], ... }
        for e in segments:
            # logger.info(str(e))
            from_to_segments_dict[e.from_vertex].append(e)
        new_plans = []
        for segment in from_to_segments_dict[start]:
            p = Plan(init_vehicle_positions)
            if p.add_segment(segment):
                new_plans.append(p)
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
                    if p.is_legal_final_plan(init_vehicle_positions):
                        final_plans.append(p)
                else:
                    for e in from_to_segments_dict[p.route[-1].to_vertex]:
                        new_plan = p.copy()
                        if new_plan.add_segment(e):
                            partial_plans.append(new_plan)
            new_plans = partial_plans
        logger.info('Made ' + str(len(final_plans)) + ' plans')
        return final_plans


class Planner():
    def __init__(self, generator=Generator, router=RichRouter):
        self.generator = generator()
        self.router = router()

    @staticmethod
    def has_no_double_biking(plan):
        route_without_waiting = [s for s in plan.route if s.transport_type != TransportType.WAIT]
        for index, segment in enumerate(route_without_waiting[:-1]):
            if route_without_waiting[index].transport_type == TransportType.BIKE and \
               route_without_waiting[index+1].transport_type == TransportType.BIKE:
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
        segments = self.generator.create_edges(start, end, fix_time)
        # for s in segments:
        #     logger.info('Segment: ' + str(s))

        vehicle_positions = VehiclePositions()

        # put a bicycle and car at home...
        vehicle_positions.add_vehicle(start.location, Vehicle(TransportType.BIKE, VehicleType.BIKE))
        vehicle_positions.add_vehicle(start.location, Vehicle(TransportType.CAR, VehicleType.CAR))

        # add OV fietsen
        ov_fiets_stations = OvFietsStations()
        vehicle_positions = ov_fiets_stations.add_default_ovfiets_positions(vehicle_positions, segments)

        plans = self.router.make_plans(start, end, segments, vehicle_positions)
        plans = list(filter(self.has_no_double_biking, plans))
        order_and_select(plans, user_preferences, fix_time)
        self.remove_unnecessary_waiting(plans, fix_time)
        log_end = time.time()
        logger.info('END - time: ' + str(log_end - log_start))
        return plans
