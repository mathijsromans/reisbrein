from datetime import datetime, timedelta
from geopy.distance import vincenty
from reisbrein.segment import Segment, TransportType


class WalkGenerator:
    SPEED_KM_H = 6
    SPEED = SPEED_KM_H / 3.6  # m/s

    def __init__(self):
        pass

    def create_segment(self, start, end):
        distance = vincenty(start.location.gps(), end.location.gps()).meters
        delta_t = timedelta(seconds=distance / WalkGenerator.SPEED)
        end.time = start.time + delta_t
        segment = Segment(TransportType.WALK, start, end, delta_t.total_seconds()/60)
        return segment

    def create_segments(self, segments):
        segments = [Segment(TransportType.BIKE, 'a', 'b', 20),
                 Segment(TransportType.TRAIN, 'a', 'c', 80),
                 Segment(TransportType.TRAIN, 'a', 'd', 50),
                 Segment(TransportType.TRAIN, 'b', 'c', 10),
                 Segment(TransportType.BIKE, 'c', 'e', 30),
                 Segment(TransportType.TRAIN, 'd', 'e', 40),
                 Segment(TransportType.CAR, 'a', 'e', 70)]
        return segments