from datetime import timedelta
from geopy.distance import vincenty
from reisbrein.api.ovfiets import OvFietsStations
from reisbrein.primitives import Segment, TransportType, Point
from reisbrein.api.weather import WeatherApi
from reisbrein.api import yoursapi
from .gen_common import FixTime, create_wait_and_move_segments
import logging


logger = logging.getLogger(__name__)


class WalkGenerator:
    SPEED_KM_H_WALK = 6
    SPEED_KM_H_BIKE = 15
    MAX_SPEED_KM_H_BIKE = 22
    SPEED_WALK = SPEED_KM_H_WALK / 3.6  # m/s
    SPEED_BIKE = SPEED_KM_H_BIKE / 3.6  # m/s
    MAX_SPEED_BIKE = MAX_SPEED_KM_H_BIKE / 3.6  # m/s
    OV_FIETS_API = OvFietsStations()
    weather = WeatherApi()

    @staticmethod
    def create_segment(start, end, fix, transport_type):
        distance = vincenty(start.location.gps(), end.location.gps()).meters
        # print ('distance in meters ' + str(distance))
        if transport_type == TransportType.WALK:
            time_sec = distance/WalkGenerator.SPEED_WALK
            map_url = ''
        else:  # transport_type == TransportType.BIKE or transport_type == TransportType.OVFIETS:
            time_sec = yoursapi.travel_time(start.location, end.location, yoursapi.Mode.BIKE)
            time_sec_min = distance/WalkGenerator.MAX_SPEED_BIKE
            if time_sec < time_sec_min:
                logger.error('Yoursapi gives unrealistic bike timing of ' +
                             str(timedelta(seconds=time_sec)) + ' from: ' +
                             str(start.location) + ' at ' + str(start.location.gps()) + ' to: ' +
                             str(end.location) + ' at ' + str(end.location.gps()))
                time_sec = distance/WalkGenerator.SPEED_BIKE
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
        edges += create_wait_and_move_segments(self, start, end, FixTime.START, TransportType.WALK)
        edges += create_wait_and_move_segments(self, start, end, FixTime.START, TransportType.BIKE)

        public_types = [TransportType.TRAIN, TransportType.TRAM, TransportType.BUS]
        train_edges = [e for e in edges if e.transport_type in public_types]
        stops_1 = set([e.from_vertex for e in train_edges])
        stops_2 = set([e.to_vertex for e in train_edges])
        for s in stops_1:
            edges += create_wait_and_move_segments(self, start, s, FixTime.END, TransportType.WALK)
            edges += create_wait_and_move_segments(self, start, s, FixTime.END, TransportType.BIKE)

        for s in stops_2:
            edges += create_wait_and_move_segments(self, s, end, FixTime.START, TransportType.WALK)
            bike_type = TransportType.BIKE
            if WalkGenerator.OV_FIETS_API.has_ovfiets(s.location.loc_str):
                bike_type = TransportType.OVFIETS
            edges += create_wait_and_move_segments(self, s, end, FixTime.START, bike_type)

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

