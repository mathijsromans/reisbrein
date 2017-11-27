from geopy.distance import vincenty
from reisbrein.api.rdwapi import RdwApi
from reisbrein.primitives import Segment, TransportType, Point
from reisbrein.generator.gen_car import CarGenerator
from reisbrein.generator.gen_walk import WalkGenerator
from reisbrein.generator.gen_public import PublicGenerator
from .gen_common import FixTime

class ParkRideGenerator:
    def __init__(self):
        self.rdwapi = RdwApi()
        self.cargenerator = CarGenerator()
        self.walkgenerator = WalkGenerator()
        self.publicgenerator = PublicGenerator()

    def closest_parking(self, location):
        parkings = self.rdwapi.get_park_and_rides()
        return min(parkings, key=lambda x: vincenty(location.gps(), x.gps()).meters, default=None)

    def create_edges(self, start, end, edges):
        for loc in (start.location, end.location):
            park_loc = self.closest_parking(loc)
            if park_loc:
                park = Point(park_loc, end.time)
                segment, new_point = self.cargenerator.create_segment(start, park, FixTime.START)
                public_edges = []
                self.publicgenerator.create_edges(new_point, end, public_edges)
                if public_edges:
                    first_vertex = min(public_edges, key=lambda x: x.from_vertex.time)

                    # walk from P+R to first public transport
                    walk_segment, new_point = self.walkgenerator.create_segment(park, first_vertex.from_vertex, FixTime.END, TransportType.WALK)

                    edges += public_edges
                    edges.append(walk_segment)
                    # transportation to parking will be added later...
