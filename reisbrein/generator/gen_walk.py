from datetime import timedelta
from geopy.distance import vincenty
from reisbrein.segment import Segment, TransportType
from reisbrein.planner import Point
from .gen_common import FixTime


class WalkGenerator:
    SPEED_KM_H_WALK = 6
    SPEED_KM_H_BIKE = 20
    SPEED_WALK = SPEED_KM_H_WALK / 3.6  # m/s
    SPEED_BIKE = SPEED_KM_H_BIKE / 3.6  # m/s

    def create_segment(self, start, end, fix, speed, transport_type):
        distance = vincenty(start.location.gps(), end.location.gps()).meters
        # print ('distance in meters ' + str(distance))
        delta_t = timedelta(seconds=distance / speed)
        if fix == FixTime.START:
            new_point = Point(end.location, start.time + delta_t)
        else:
            new_point = Point(start.location, end.time - delta_t)
        segment = Segment(transport_type, start, end, delta_t.total_seconds()/60)
        return segment, new_point

    def create_edges(self, start, end, edges):
        public_types = [TransportType.TRAIN, TransportType.TRAM, TransportType.BUS]
        train_edges = [e for e in edges if e.transport_type in public_types]
        stops_1 = set([e.from_vertex for e in train_edges])
        stops_2 = set([e.to_vertex for e in train_edges])
        for s in stops_1:
            # walk to first station
            segment, new_point = self.create_segment(start, s, FixTime.END, WalkGenerator.SPEED_WALK, TransportType.WALK)
            if new_point.time > start.time:
                edges.append(Segment(TransportType.WAIT, start, new_point, (new_point.time-start.time).total_seconds()/60))
                edges.append(Segment(TransportType.WALK, new_point, s, (s.time-new_point.time).total_seconds()/60))
            # bike to first station
            segment, new_point = self.create_segment(start, s, FixTime.END, WalkGenerator.SPEED_BIKE, TransportType.BIKE)
            if new_point.time > start.time:
                edges.append(Segment(TransportType.WAIT, start, new_point, (new_point.time-start.time).total_seconds()/60))
                edges.append(Segment(TransportType.BIKE, new_point, s, (s.time-new_point.time).total_seconds()/60))

        for s in stops_2:
            # walk from second station
            segment, new_point = self.create_segment(s, end, FixTime.START, WalkGenerator.SPEED_WALK, TransportType.WALK)
            # print('Created segment ' + str(segment) + ' new point time ' + str(new_point.time))
            if new_point.time < end.time:
                # print('Within time ' + str(segment))
                edges.append(Segment(TransportType.WALK, s, new_point, (new_point.time-s.time).total_seconds()/60))
                edges.append(Segment(TransportType.WAIT, new_point, end, (end.time-new_point.time).total_seconds()/60))
            # bike from second station
            segment, new_point = self.create_segment(s, end, FixTime.START, WalkGenerator.SPEED_BIKE, TransportType.BIKE)
            if new_point.time < end.time:
                edges.append(
                    Segment(TransportType.BIKE, s, new_point, (new_point.time - s.time).total_seconds() / 60))
                edges.append(
                    Segment(TransportType.WAIT, new_point, end, (end.time - new_point.time).total_seconds() / 60))
