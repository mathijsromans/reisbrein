from .graph import Edge
from enum import Enum


class TransportType(Enum):
    WAIT = 0
    WALK = 1
    TRAIN = 2
    BIKE = 3
    CAR = 4


class Segment(Edge):
    def __init__(self, transport_type, from_vertex, to_vertex, distance):
        super(Segment, self).__init__(from_vertex, to_vertex, distance)
        self.transport_type = transport_type

