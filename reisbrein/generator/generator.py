import datetime
import logging
from reisbrein.primitives import Segment, TransportType, Point, Location
from reisbrein.generator.gen_public import PublicGenerator
from reisbrein.generator.gen_walk import WalkGenerator
from reisbrein.generator.gen_car import CarGenerator
from reisbrein.generator.gen_parkride import ParkRideGenerator
from reisbrein.api.monotchapi import MonotchApi

logger = logging.getLogger(__name__)


class LocationHolder:
    """Locations created by data from different sources can contain (near) duplicates
    To prevent this, locations should be created or processed by this LocationHolder,
    which will eliminate the duplicates.
    """

    def __init__(self):
        self.existing_locations = {}  # {name_without_spaces: location}

    def create_location(self, loc_str, gps=None):
        return self.process(Location(loc_str, gps))

    def process(self, arg):
        MAX_DISTANCE = 200  # max distance for locations to be possibly counted as identical
        if type(arg) is list:
            return [self.process(location) for location in arg]
        assert isinstance(arg, Location)
        name_without_spaces = arg.loc_str.replace(' ', '')
        existing = self.existing_locations.get(name_without_spaces)
        if existing:
            if arg.distance_to(existing).meters < MAX_DISTANCE:
                # if arg != existing:
                #     logger.info('New location \"' + str(arg) + '\" is not identical but equivalent to
                #       \"' + str(existing) + '\" (distance = ' + str(arg.distance_to(existing).meters) + ' meters)')
                return existing  # too similar, discard new location and use existing location
            if arg.distance_to(existing).meters < 2*MAX_DISTANCE:
                logger.error('WARNING: New location \"' + str(arg) + '\" is very similar to \"' + str(existing) +
                             '\" (distance = ' + str(arg.distance_to(existing).meters) + ' meters)')
        self.existing_locations[name_without_spaces] = arg
        return arg


class Generator:
    def __init__(self):
        self.walk_generator = WalkGenerator()
        self.car_generator = CarGenerator()
        self.location_holder = LocationHolder()

    @staticmethod
    def remove_duplicates(edges):
        points = []
        for e in edges:
            points.append(e.from_vertex)
            points.append(e.to_vertex)
        locations = [p.location for p in points]

        # remove duplicate locations
        for index, l1 in enumerate(locations):
            for l2 in locations[index+1:]:
                if l1 is not l2 and l1 == l2:
                    for p in points:
                        if p.location is l2:
                            p.location = l1

        # remove duplicate points
        for index, p1 in enumerate(points):
            for p2 in points[index+1:]:
                if not p1 is p2 and p1 == p2:
                    for e in edges:
                        if e.from_vertex is p2:
                            e.from_vertex = p1
                        if e.to_vertex is p2:
                            e.to_vertex = p1

        # remove duplicate segments
        duplicates = set()
        for index, e1 in enumerate(edges):
            for e2 in edges[index+1:]:
                if e1.has_same_points_and_type(e2):
                    duplicates.add(e2)
        edges[:] = [e for e in edges if e not in duplicates]

    def create_edges(self, start, end, fix_time):
        start.location = self.location_holder.process(start.location)
        end.location = self.location_holder.process(end.location)

        edges = []

        routing_api = MonotchApi()
        public_generator = PublicGenerator(routing_api, self.location_holder)
        parkride_generator = ParkRideGenerator(public_generator, self.location_holder)
        pub_request = public_generator.prepare_request(start, end, fix_time)
        park_request = parkride_generator.prepare_request(start, end, fix_time)

        routing_api.do_requests()

        pub_request.finish(edges)
        park_request.finish(edges)

        self.walk_generator.create_edges(start, end, fix_time, edges)
        self.car_generator.create_edges(start, end, fix_time, edges)
        self.remove_duplicates(edges)
        # for e in edges:
        #     logger.info(e)
        return edges


class TestGenerator:

    def create_edges(self, start, end, fix_time):
        b = Point('b', start.time+datetime.timedelta(seconds=20))
        c = Point('c', start.time+datetime.timedelta(seconds=80))
        d = Point('d', start.time+datetime.timedelta(seconds=50))
        edges = [Segment(TransportType.BIKE, start, b),
                 Segment(TransportType.TRAIN, start, c),
                 Segment(TransportType.TRAIN, start, d),
                 Segment(TransportType.TRAIN, b, c),
                 Segment(TransportType.BIKE, c, end),
                 Segment(TransportType.TRAIN, d, end),
                 Segment(TransportType.CAR, start, end)]
        return edges
