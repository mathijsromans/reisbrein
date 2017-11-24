import datetime
from reisbrein.primitives import Segment, TransportType, Point
from reisbrein.generator.gen_public import PublicGenerator
from reisbrein.generator.gen_walk import WalkGenerator
from reisbrein.generator.gen_car import CarGenerator
from reisbrein.generator.gen_parkride import ParkRideGenerator


class Generator:
    def __init__(self):
        self.walk_generator = WalkGenerator()
        self.public_generator = PublicGenerator()
        self.car_generator = CarGenerator()
        self.parkride_generator = ParkRideGenerator()

    def create_edges(self, start, end):
        edges = []
        self.public_generator.create_edges(start, end, edges)
        self.parkride_generator.create_edges(start, end, edges)
        self.walk_generator.create_edges(start, end, edges)
        self.car_generator.create_edges(start, end, edges)
        # for e in edges:
        #     print(e)
        return edges


class TestGenerator:

    def create_edges(self, start, end):
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
