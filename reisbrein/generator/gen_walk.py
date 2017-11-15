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

    def create_edges(self, segments):
        segments = []
        return segments