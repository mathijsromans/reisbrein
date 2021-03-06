from datetime import timedelta
from reisbrein.api.tomtom import TomTomApi
from reisbrein.primitives import Segment, TransportType, Point
from .gen_common import FixTime, create_wait_and_move_segments


class CarGenerator:

    def __init__(self):
        self.tomtom = TomTomApi()
        
    

    def create_segment(self, start, end, fix, transport_type=TransportType.CAR, option=False):
        route_params = TomTomApi.RouteParams(start=start.location, end=end.location, avoid_highways=option)
        travel_time, delay = self.tomtom.travel_time(route_params)
        delta_t = timedelta(seconds=travel_time)
        map_url = self.tomtom.map_url(route_params)
        if fix == FixTime.START:
            new_point = Point(end.location, start.time + delta_t)
            segment = Segment(transport_type, start, new_point)
        else:
            new_point = Point(start.location, end.time - delta_t)
            segment = Segment(transport_type, new_point, end)
        segment.delay = delay/60
        segment.map_url = map_url
        return segment, new_point

    def create_edges(self, start, end, fix_time, edges):
        new_edges = []
        
        #both including and excluding highways, to possibly filter later on
        # for avoid_highways in (True, False):
        for avoid_highways in [False]:

            new_edges += create_wait_and_move_segments(self, start, end, fix_time, TransportType.CAR, option=avoid_highways)

            for e in edges:
                if e.from_vertex.location.has_parking:
                    new_edges += create_wait_and_move_segments(self, start, e.from_vertex, FixTime.END, TransportType.CAR, option=avoid_highways)

        edges += new_edges