from datetime import timedelta
from geopy.distance import vincenty
from reisbrein.segment import Segment, TransportType
from reisbrein.planner import Point
from enum import Enum


class WalkGenerator:
    SPEED_KM_H = 6
    SPEED = SPEED_KM_H / 3.6  # m/s

    class FixTime(Enum):
        START = 0
        END = 1

    def create_segment(self, start, end, fix):
        distance = vincenty(start.location.gps(), end.location.gps()).meters
        delta_t = timedelta(seconds=distance / WalkGenerator.SPEED)
        if fix == WalkGenerator.FixTime.START:
            new_point = Point(end.location, start.time + delta_t)
        else:
            new_point = Point(start.location, end.time - delta_t)
        segment = Segment(TransportType.WALK, start, end, delta_t.total_seconds()/60)
        return segment, new_point

    def create_edges(self, start, end, edges):
        stops_1 = set([e.from_vertex for e in edges])
        stops_2 = set([e.to_vertex for e in edges])
        for s in stops_1:
            # walk to first station
            segment, new_point = self.create_segment(start, s, WalkGenerator.FixTime.END)
            if new_point.time > start.time:
                edges.append(Segment(TransportType.WAIT, start, new_point, (new_point.time-start.time).total_seconds()/60))
                edges.append(Segment(TransportType.WALK, new_point, s, (s.time-new_point.time).total_seconds()/60))
        for s in stops_2:
            # walk from second station
            segment, new_point = self.create_segment(s, end, WalkGenerator.FixTime.START)
            if new_point.time < end.time:
                edges.append(Segment(TransportType.WALK, s, new_point, (new_point.time-s.time).total_seconds()/60))
                edges.append(Segment(TransportType.WAIT, new_point, end, (end.time-new_point.time).total_seconds()/60))
