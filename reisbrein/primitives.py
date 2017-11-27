from .graph import Edge
from enum import Enum
from reisbrein.api.tomtom import TomTomApi
import datetime

def noon_today():
    return datetime.datetime.combine(datetime.date.today(), datetime.time(12))

class TransportType(Enum):
    WAIT = 0
    WALK = 1
    TRAIN = 2
    BIKE = 3
    CAR = 4
    BUS = 5
    TRAM = 6
    OVFIETS = 7


class Location:
    def __init__(self, loc_str, location=(0,0)):
        # geolocator = Nominatim()
        self.loc_str = loc_str
        self.location = location if location != (0,0) else TomTomApi().search(loc_str)
        self.has_parking = False
        # geolocator.geocode(self.loc_str)

    def gps(self):
        return self.location

    def __str__(self):
        return self.loc_str

    @property
    def latitude(self):
        return self.location.latitude

    @property
    def longitude(self):
        return self.location.longitude


class Point:
    def __init__(self, location, time):
        self.location = location
        self.time = time

    def __str__(self):
        return str(self.location) + ' @ ' + str(self.time_sec)


class Segment(Edge):
    def __init__(self, transport_type, start, end):
        super(Segment, self).__init__(start, end, (end.time - start.time).total_seconds())
        self.transport_type = transport_type
        self.weather = ''
        self.weather_icon = ''
        self.delay = 0
        self.map_url = ''

    def __lt__(self, other):
        return self.time < other.time_sec

    def __str__(self):
        return '['+str(self.transport_type)+ ' ' + str(self.weather) + '] '+str(self.from_vertex)+' --> '+str(self.to_vertex)

