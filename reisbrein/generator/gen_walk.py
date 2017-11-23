from datetime import timedelta
from geopy.distance import vincenty
from reisbrein.api.ovfiets import OvFietsStations
from reisbrein.segment import Segment, TransportType
from reisbrein.planner import Point
from reisbrein.api.weather import WeatherApi
from reisbrein.api import yoursapi
from .gen_common import FixTime


class WalkGenerator:
    SPEED_KM_H_WALK = 6
    SPEED_KM_H_BIKE = 15
    SPEED_WALK = SPEED_KM_H_WALK / 3.6  # m/s
    SPEED_BIKE = SPEED_KM_H_BIKE / 3.6  # m/s
    OV_FIETS_API = OvFietsStations()
    weather = WeatherApi()

    def create_segment(self, start, end, fix, transport_type):
        distance = vincenty(start.location.gps(), end.location.gps()).meters
        # print ('distance in meters ' + str(distance))
        if transport_type == TransportType.WALK:
            time_sec = distance/WalkGenerator.SPEED_WALK
            map_url = ''
        else:  # transport_type == TransportType.BIKE:
            time_sec = yoursapi.travel_time(start.location, end.location, yoursapi.Mode.BIKE)
            map_url = yoursapi.map_url(start.location, end.location, yoursapi.Mode.BIKE)
        delta_t = timedelta(seconds=time_sec)
        if fix == FixTime.START:
            new_point = Point(end.location, start.time + delta_t)
            segment = Segment(transport_type, start, new_point)
        else:
            new_point = Point(start.location, end.time - delta_t)
            segment = Segment(transport_type, new_point, end)
        segment.map_url = map_url
        return segment, new_point

    def do_create_edges(self, start, end, edges):
        # walk begin to end
        segment, new_point = self.create_segment(start, end, FixTime.START, TransportType.WALK)
        if new_point.time < end.time:
            edges.append(segment)
            edges.append(Segment(TransportType.WAIT, new_point, end))
        # bike begin to end
        segment, new_point = self.create_segment(start, end, FixTime.START, TransportType.BIKE)
        if new_point.time < end.time:
            edges.append(segment)
            edges.append(Segment(TransportType.WAIT, new_point, end))

        public_types = [TransportType.TRAIN, TransportType.TRAM, TransportType.BUS]
        train_edges = [e for e in edges if e.transport_type in public_types]
        stops_1 = set([e.from_vertex for e in train_edges])
        stops_2 = set([e.to_vertex for e in train_edges])
        for s in stops_1:
            # walk to first station
            segment, new_point = self.create_segment(start, s, FixTime.END, TransportType.WALK)
            if new_point.time > start.time:
                edges.append(Segment(TransportType.WAIT, start, new_point))
                edges.append(segment)

            # bike to first station
            segment, new_point = self.create_segment(start, s, FixTime.END, TransportType.BIKE)
            if new_point.time > start.time:
                edges.append(Segment(TransportType.WAIT, start, new_point))
                edges.append(segment)

        for s in stops_2:
            # walk from second station
            segment, new_point = self.create_segment(s, end, FixTime.START, TransportType.WALK)
            if new_point.time < end.time:
                edges.append(segment)
                edges.append(Segment(TransportType.WAIT, new_point, end))
            # bike from second station
            bike_type = TransportType.BIKE
            if WalkGenerator.OV_FIETS_API.has_ovfiets(s.location.loc_str):
                bike_type = TransportType.OVFIETS
            segment, new_point = self.create_segment(s, end, FixTime.START, TransportType.BIKE)
            if new_point.time < end.time:
                edges.append(segment)
                edges.append(Segment(TransportType.WAIT, new_point, end))

    @staticmethod
    def add_weather(edges):
        for e in edges:
            words = e.from_vertex.location.loc_str.replace(',', '').split()
            for w in words:
                if e.weather:
                    break
                e.weather, e.weather_icon = WalkGenerator.weather.search(w)

    def create_edges(self, start, end, edges):
        self.do_create_edges(start, end, edges)
        # self.add_weather(edges)

