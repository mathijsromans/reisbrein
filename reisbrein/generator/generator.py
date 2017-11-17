from reisbrein.segment import Segment, TransportType
from reisbrein.generator.gen_public import PublicGenerator
from reisbrein.generator.gen_walk import WalkGenerator
from reisbrein.generator.gen_car import CarGenerator


class Generator:
    def __init__(self):
        self.walk_generator = WalkGenerator()
        self.public_generator = PublicGenerator()
        self.car_generator = CarGenerator()

    def create_edges(self, start, end):
        edges = []
        self.public_generator.create_edges(start, end, edges)
        self.walk_generator.create_edges(start, end, edges)
        self.car_generator.create_edges(start, end, edges)
        return edges


class TestGenerator:

    def create_edges(self, start, end):
        edges = [Segment(TransportType.BIKE, start, 'b', 20),
                 Segment(TransportType.TRAIN, start, 'c', 80),
                 Segment(TransportType.TRAIN, start, 'd', 50),
                 Segment(TransportType.TRAIN, 'b', 'c', 10),
                 Segment(TransportType.BIKE, 'c', end, 30),
                 Segment(TransportType.TRAIN, 'd', end, 40),
                 Segment(TransportType.CAR, start, end, 70)]
        return edges
