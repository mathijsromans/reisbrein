from datetime import timedelta
from reisbrein.api.tomtom import TomTomApi
from reisbrein.planner import Point
from reisbrein.segment import Segment, TransportType
from .gen_common import FixTime


class CarGenerator:

    def __init__(self):
        self.tomtom = TomTomApi()

    def create_segment(self, start, end, fix):
        travel_time, delay = self.tomtom.travel_time(start.location, end.location)
        delta_t = timedelta(seconds=travel_time)
        if fix == FixTime.START:
            new_point = Point(end.location, start.time + delta_t)
        else:
            new_point = Point(start.location, end.time - delta_t)
        segment = Segment(TransportType.CAR, start, new_point, delta_t.total_seconds()/60)
        segment.delay = delay/60
        return segment, new_point

    def create_edges(self, start, end, edges):
        segment, new_point = self.create_segment(start, end, FixTime.START)
        if new_point.time < end.time:
            edges.append(segment)
            edges.append(Segment(TransportType.WAIT, new_point, end, (end.time - new_point.time).total_seconds() / 60))
