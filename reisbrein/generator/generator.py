from reisbrein.segment import Segment, TransportType
from reisbrein.generator.gen_train import TrainGenerator
from reisbrein.generator.gen_walk import WalkGenerator

class TestGenerator:
    def __init__(self):
        generators = [
            TrainGenerator(),
            WalkGenerator()
        ]

    def create_edges(self, start, end):
        edges = [Segment(TransportType.BIKE, start, 'b', 20),
                 Segment(TransportType.TRAIN, start, 'c', 80),
                 Segment(TransportType.TRAIN, start, 'd', 50),
                 Segment(TransportType.TRAIN, 'b', 'c', 10),
                 Segment(TransportType.BIKE, 'c', end, 30),
                 Segment(TransportType.TRAIN, 'd', end, 40),
                 Segment(TransportType.CAR, start, end, 70)]
        return edges
