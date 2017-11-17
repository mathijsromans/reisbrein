from datetime import timedelta
from reisbrein.api.tomtom import TomTomApi
from reisbrein.planner import Point
from reisbrein.segment import Segment, TransportType
from .gen_common import FixTime


class CarGenerator:

    def __init__(self):
        self.tomtom = TomTomApi()

    def create_segment(self, start, end, fix):
        delta_t = timedelta(seconds=self.tomtom.travel_time(start.location, end.location))
        if fix == FixTime.START:
            new_point = Point(end.location, start.time + delta_t)
        else:
            new_point = Point(start.location, end.time - delta_t)
        segment = Segment(TransportType.CAR, start, end, delta_t.total_seconds()/60)
        return segment, new_point

    def create_edges(self, start, end, edges):
        segment, new_point = self.create_segment(start, end, FixTime.START)
        if new_point.time < end.time:
            edges.append(Segment(TransportType.CAR, start, new_point, (new_point.time - start.time).total_seconds() / 60))
            edges.append(Segment(TransportType.WAIT, new_point, end, (end.time - new_point.time).total_seconds() / 60))
