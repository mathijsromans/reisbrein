from collections import namedtuple
from geopy.distance import vincenty
from reisbrein.api.rdwapi import RdwApi
from reisbrein.primitives import Segment, TransportType, Point
from reisbrein.generator.gen_car import CarGenerator
from reisbrein.generator.gen_walk import WalkGenerator
from reisbrein.generator.gen_public import PublicGenerator
from .gen_common import FixTime


class ParkRideGenerator:
    ParkPointAndGenerator = namedtuple('ParkPointAndGenerator', ['park_point', 'generator'])

    def __init__(self, start, end, fix_time, public_generator_cls=PublicGenerator):
        self.start = start
        self.end = end
        self.fix_time = fix_time
        self.rdwapi = RdwApi()
        self.cargenerator = CarGenerator()
        self.walkgenerator = WalkGenerator()
        self.ppags = []
        self.public_generator_cls = public_generator_cls

    def closest_parking(self, location):
        parkings = self.rdwapi.get_park_and_rides()
        return min(parkings, key=lambda x: vincenty(location.gps, x.gps).meters, default=None)

    def prepare(self, routing_api):
        for loc in {self.start.location, self.end.location}:
            park_loc = self.closest_parking(loc)
            if park_loc:
                park = Point(park_loc, self.end.time)
                segment, new_point = self.cargenerator.create_segment(self.start, park, FixTime.START)
                publicgenerator = self.public_generator_cls(new_point, self.end, self.fix_time)
                publicgenerator.prepare(routing_api)
                ppag = self.ParkPointAndGenerator(park, publicgenerator)
                self.ppags.append(ppag)

    def finish(self, edges):
        for ppag in self.ppags:
            num_edges = len(edges)
            ppag.generator.finish(edges)
            if len(edges) > num_edges:
                first_new_vertex = min(edges[num_edges:], key=lambda x: x.from_vertex.time)

                # walk from P+R to first public transport
                walk_segment, new_point = self.walkgenerator.create_segment(ppag.park_point, first_new_vertex.from_vertex, FixTime.END, TransportType.WALK)
                edges.append(walk_segment)
                # transportation to parking will be added later...

