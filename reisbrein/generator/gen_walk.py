from datetime import timedelta
from geopy.distance import vincenty
from reisbrein.segment import Segment, TransportType
from enum import Enum


class WalkGenerator:
    SPEED_KM_H = 6
    SPEED = SPEED_KM_H / 3.6  # m/s

    class FixTime(Enum):
        START = 0
        END = 1

    def __init__(self):
        pass

    def create_segment(self, start, end, fix):
        distance = vincenty(start.location.gps(), end.location.gps()).meters
        delta_t = timedelta(seconds=distance / WalkGenerator.SPEED)
        if fix == WalkGenerator.FixTime.START:
            end.time = start.time + delta_t
        else:
            start.time = end.time - delta_t
        segment = Segment(TransportType.WALK, start, end, delta_t.total_seconds()/60)
        return segment

    def create_edges(self, start, end, edges):
        end.time = start.time + timedelta(minutes=50)
        stops_1 = set([e.from_vertex for e in edges])
        stops_2 = set([e.to_vertex for e in edges])
        for s in stops_1:
            # walk to first station
            edges.append(Segment(TransportType.WALK, start, s, 10))
        for s in stops_2:
            # walk from second station
            edges.append(Segment(TransportType.WALK, s, end, 10))
