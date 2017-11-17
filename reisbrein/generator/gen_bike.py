from datetime import timedelta
from geopy.distance import vincenty
from reisbrein.segment import Segment, TransportType
from reisbrein.planner import Point
from .gen_common import FixTime


class BikeGenerator:
    SPEED_KM_H = 20
    SPEED = SPEED_KM_H / 3.6  # m/s

    def create_segment(self, start, end, fix):
        distance = vincenty(start.location.gps(), end.location.gps()).meters
        delta_t = timedelta(seconds=distance / BikeGenerator.SPEED)
        if fix == FixTime.START:
            new_point = Point(end.location, start.time + delta_t)
        else:
            new_point = Point(start.location, end.time - delta_t)
        segment = Segment(TransportType.BIKE, start, end, delta_t.total_seconds()/60)
        return segment, new_point

    def create_edges(self, start, end, edges):
        train_edges = [e for e in edges if e.transport_type == TransportType.TRAIN]
        stops_1 = set([e.from_vertex for e in train_edges])
        stops_2 = set([e.to_vertex for e in train_edges])
        for s in stops_1:
            # walk to first station
            segment, new_point = self.create_segment(start, s, FixTime.END)
            if new_point.time > start.time:
                edges.append(Segment(TransportType.WAIT, start, new_point, (new_point.time-start.time).total_seconds()/60))
                edges.append(Segment(TransportType.BIKE, new_point, s, (s.time-new_point.time).total_seconds()/60))
        for s in stops_2:
            # walk from second station
            segment, new_point = self.create_segment(s, end, FixTime.START)
            if new_point.time < end.time:
                edges.append(Segment(TransportType.BIKE, s, new_point, (new_point.time-s.time).total_seconds()/60))
                edges.append(Segment(TransportType.WAIT, new_point, end, (end.time-new_point.time).total_seconds()/60))
