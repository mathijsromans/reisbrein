from datetime import timedelta
from geopy.distance import vincenty
from reisbrein.api.ovfiets import OvFietsStations
from reisbrein.primitives import Segment, TransportType, Point
from reisbrein.api.weather import WeatherApi
from reisbrein.api import yoursapi
from reisbrein.models import TravelTime
from .gen_common import FixTime, create_wait_and_move_segments
import logging
import time


logger = logging.getLogger(__name__)


class WalkGenerator:
    SPEED_KM_H_WALK = 3.5  # as the crow flies
    SPEED_KM_H_BIKE = 15
    MAX_SPEED_KM_H_BIKE = 22
    SPEED_WALK = SPEED_KM_H_WALK / 3.6  # m/s
    SPEED_BIKE = SPEED_KM_H_BIKE / 3.6  # m/s
    MAX_SPEED_BIKE = MAX_SPEED_KM_H_BIKE / 3.6  # m/s
    MIN_BIKE_TIME_SEC = 120

    OV_FIETS_API = OvFietsStations()
    weather = WeatherApi()

    @staticmethod
    def get_bike_travel_time(start_loc, end_loc, transport_type):
        if transport_type == TransportType.OVFIETS:
            transport_type = TransportType.BIKE
        start_gps = start_loc.gps
        end_gps = end_loc.gps
        distance = vincenty(start_gps, end_gps).meters
        # print ('distance in meters ' + str(distance))
        if transport_type == TransportType.WALK:
            time_sec = distance/WalkGenerator.SPEED_WALK
        else:  # transport_type == TransportType.BIKE or transport_type == TransportType.OVFIETS:
            # logger.info('Yoursapi bike request from: ' + str(start_loc) + ' to: ' + str(end_loc))
            time_sec_min = distance/WalkGenerator.MAX_SPEED_BIKE
            time_sec = yoursapi.travel_time(start_gps, end_gps, TransportType.BIKE)
            if time_sec_min > 30 and time_sec < time_sec_min:
                logger.error('Yoursapi gives unrealistic bike timing of ' +
                             str(timedelta(seconds=time_sec)) + ' from: ' +
                             str(start_loc) + ' at ' + str(start_loc.gps) + ' to: ' +
                             str(end_loc) + ' at ' + str(end_loc.gps))
                time_sec = distance/WalkGenerator.SPEED_BIKE
            else:
                TravelTime.objects.get_or_create(
                    flat = start_gps[0],
                    flon = start_gps[1],
                    tlat = end_gps[0],
                    tlon = end_gps[1],
                    transport_type = transport_type.value,
                    defaults = {
                        'distance': distance,
                        'time_sec': time_sec
                    }
                )
        return time_sec

    @staticmethod
    def create_segment(start, end, fix_time, transport_type):
        time_sec = WalkGenerator.get_bike_travel_time(start.location, end.location, transport_type)
        map_url = yoursapi.map_url(start.location, end.location, transport_type)
        delta_t = timedelta(seconds=time_sec)
        if fix_time == FixTime.START:
            new_point = Point(end.location, start.time + delta_t)
            segment = Segment(transport_type, start, new_point)
        else:
            new_point = Point(start.location, end.time - delta_t)
            segment = Segment(transport_type, new_point, end)
        segment.map_url = map_url
        return segment, new_point

    def do_create_edges(self, start, end, fix_time, edges):
        edges += create_wait_and_move_segments(self, start, end, FixTime.START, TransportType.WALK)
        edges += create_wait_and_move_segments(self, start, end, FixTime.START, TransportType.BIKE,
                                               WalkGenerator.MIN_BIKE_TIME_SEC)

        public_types = [TransportType.TRAIN, TransportType.TRAM, TransportType.BUS]
        train_edges = [e for e in edges if e.transport_type in public_types]
        stops_1 = set([e.from_vertex for e in train_edges])
        stops_2 = set([e.to_vertex for e in train_edges])
        for s in stops_1:
            edges += create_wait_and_move_segments(self, start, s, FixTime.END, TransportType.WALK)
            edges += create_wait_and_move_segments(self, start, s, FixTime.END, TransportType.BIKE,
                                                   WalkGenerator.MIN_BIKE_TIME_SEC)

        for s in stops_2:
            edges += create_wait_and_move_segments(self, s, end, FixTime.START, TransportType.WALK)
            if WalkGenerator.OV_FIETS_API.has_ovfiets(s.location.loc_str):
                bike_type = TransportType.OVFIETS
                edges += create_wait_and_move_segments(self, s, end, FixTime.START, bike_type,
                                                   WalkGenerator.MIN_BIKE_TIME_SEC)

    @staticmethod
    def add_weather(edges):
        for e in edges:
            words = e.from_vertex.location.loc_str.replace(',', '').split()
            for w in words:
                if e.weather:
                    break
                e.weather, e.weather_icon = WalkGenerator.weather.search(w)

    def create_edges(self, start, end, fix_time, edges):
        # logger.info('BEGIN')
        # log_start = time.time()
        self.do_create_edges(start, end, fix_time, edges)
        # self.add_weather(edges)
        # log_end = time.time()
        # logger.info('END - time: ' + str(log_end - log_start))

