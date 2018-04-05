from geopy.distance import vincenty
from reisbrein.api.rdwapi import RdwApi
from reisbrein.primitives import Segment, TransportType, Point
from reisbrein.generator.gen_car import CarGenerator
from reisbrein.generator.gen_walk import WalkGenerator
from .gen_common import FixTime


class ParkRideGeneratorRequest:

    def __init__(self, start, end, fix_time, public_generator, parkings):
        self.ppars = []
        cargenerator = CarGenerator()
        for loc in {start.location, end.location}:
            park_loc = self.closest_parking(loc, parkings)
            if park_loc:
                park = Point(park_loc, end.time)
                segment, new_point = cargenerator.create_segment(start, park, FixTime.START)
                request = public_generator.prepare_request(new_point, end, fix_time)
                self.ppars.append((park, request))

    @staticmethod
    def closest_parking(location, parkings):
        return min(parkings, key=lambda x: vincenty(location.gps, x.gps).meters, default=None)

    def finish(self, edges):
        walkgenerator = WalkGenerator()
        for ppar in self.ppars:
            num_edges = len(edges)
            ppar[1].finish(edges)
            if len(edges) > num_edges:
                first_new_vertex = min(edges[num_edges:], key=lambda x: x.from_vertex.time)

                # walk from P+R to first public transport
                walk_segment, new_point = walkgenerator.create_segment(ppar[0], first_new_vertex.from_vertex, FixTime.END, TransportType.WALK)
                edges.append(walk_segment)
                # transportation to parking will be added later...


class ParkRideGenerator:

    def __init__(self, public_generator, location_holder):
        self.public_generator = public_generator
        rdwapi = RdwApi()
        self.parkings = location_holder.process(rdwapi.get_park_and_rides())

    def prepare_request(self, start, end, fix_time):
        return ParkRideGeneratorRequest(start, end, fix_time, self.public_generator, self.parkings)

    def do_requests(self):
        self.public_generator.do_requests()
