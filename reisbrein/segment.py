from .graph import Edge
from enum import Enum


class TransportType(Enum):
    WAIT = 0
    WALK = 1
    TRAIN = 2
    BIKE = 3
    CAR = 4
    BUS = 5
    TRAM = 6
    OVFIETS = 7


class Segment(Edge):
    def __init__(self, transport_type, from_vertex, to_vertex, distance):
        super(Segment, self).__init__(from_vertex, to_vertex, distance)
        self.transport_type = transport_type
        self.weather = 0
        self.weather_icon = ''
        self.delay = 0

    def __lt__(self, other):
        return self.distance < other.distance

    def __str__(self):
        return '(['+str(self.transport_type)+ ' ' + str(self.weather) + '] '+str(self.from_vertex)+' --> '+str(self.to_vertex)+')'

