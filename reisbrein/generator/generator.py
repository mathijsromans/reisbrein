from reisbrein.segment import Segment, TransportType
from reisbrein.generator.gen_train import TrainGenerator
from reisbrein.generator.gen_walk import WalkGenerator


class Generator:
    def __init__(self):
        self.walk_generator = WalkGenerator()
        self.train_generator = TrainGenerator()

    def create_edges(self, start, end):
        edges = []
        self.train_generator(edges, start, end)
        self.walk_generator(edges, start, end)
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
