from .graph import Edge
from enum import Enum


class TransportType(Enum):
    TRAIN = 1
    BIKE = 2
    CAR = 3


class Segment(Edge):
    def __init__(self, transport_type, from_vertex, to_vertex, distance):
        super(Segment, self).__init__(from_vertex, to_vertex, distance)
        self.transport_type = transport_type

