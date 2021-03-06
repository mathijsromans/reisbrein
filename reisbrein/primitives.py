import datetime
import logging
from geopy.distance import vincenty
from .graph import BasicEdge
from enum import Enum
from reisbrein.api.tomtom import TomTomApi


logger = logging.getLogger(__name__)


class _CaptureEq:
    """ Object wrapper that remembers "other" for successful equality tests.
        From: http://code.activestate.com/recipes/499299/
    """
    def __init__(self, obj):
        self.obj = obj
        self.match = obj

    def __eq__(self, other):
        result = (self.obj == other)
        if result:
            self.match = other
        return result

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.obj)


def get_equivalent(container, item, default=None):
    """Gets the specific container element matched by: "item in container".

    Useful for retreiving a canonical value equivalent to "item".  For example, a
    caching or interning application may require fetching a single representative
    instance from many possible equivalent instances).

    >>> get_equivalent(set([1, 2, 3]), 2.0)             # 2.0 is equivalent to 2
    2
    >>> get_equivalent([1, 2, 3], 4, default=0)
    0
    """
    t = _CaptureEq(item)
    if t in container:
        return t.match
    return default


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
    INVISIBLE_WAIT = 8

    def needs_vehicle(self):
        return self == self.BIKE or\
               self == self.CAR or\
               self == self.OVFIETS

    def to_dutch(self):
        translate = {
            TransportType.WAIT: 'Wachten',
            TransportType.WALK: 'Lopen',
            TransportType.TRAIN: 'Trein',
            TransportType.BIKE: 'Fiets',
            TransportType.CAR: 'Auto',
            TransportType.BUS: 'Bus',
            TransportType.TRAM: 'Tram',
            TransportType.OVFIETS: 'OV-fiets',
            TransportType.INVISIBLE_WAIT: 'Wachten (buiten reis)',
        }
        try:
            return translate[self]
        except KeyError:
            return ''


class Location:
    def __init__(self, loc_str, gps=None):
        # geolocator = Nominatim()
        self.loc_str = loc_str
        self._gps = gps if gps else TomTomApi().search(loc_str)
        self.has_parking = False
        # geolocator.geocode(self.loc_str)

    @classmethod
    def midpoint(cls, loc1, loc2, p=0.5):
        loc_str = 'mid_' + loc1.loc_str + '_' + loc2.loc_str
        gps = ((1-p)*loc1.gps[0] + p*loc2.gps[0],
               (1-p)*loc1.gps[1] + p*loc2.gps[1])
        return cls(loc_str, gps)

    @property
    def gps(self):
        return self._gps

    @property
    def latitude(self):
        return self.gps.latitude

    @property
    def longitude(self):
        return self.gps.longitude

    def distance_to(self, other):
        return vincenty(self.gps, other.gps)

    def __eq__(self, other):
        # see https://stackoverflow.com/a/25176504
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return self.loc_str

    def full_str(self):
        return self.loc_str + '@' + str(self.gps)


class Point:
    def __init__(self, location, time):
        self.location = location
        self.time = time

    def __eq__(self, other):
        # see https://stackoverflow.com/a/25176504
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))

    def __str__(self):
        return str(self.location) + ' @ ' + str(self.time)


class VehicleType(Enum):
    CAR = 0
    BIKE = 1
    OVFIETS = 2

    def __str__(self):
        translate = {
            VehicleType.CAR: 'Car',
            VehicleType.BIKE: 'Bike',
            VehicleType.OVFIETS: 'OVFiets',
        }
        try:
            return translate[self]
        except KeyError:
            return ''


class Vehicle:
    def __init__(self, transport_type, vehicle_type):
        self.transport_type = transport_type
        self.vehicle_type = vehicle_type

    def __repr__(self):
        return 'Vehicle ' + str(id(self)) + ' ' + str(self.vehicle_type)


class Segment(BasicEdge):

    def __init__(self, transport_type, start, end):
        super(Segment, self).__init__(start, end, )
        self.transport_type = transport_type
        self.weather = ''
        self.weather_icon = ''
        self.delay = 0
        self.map_url = ''
        self.route_name = ''
        self.platform_code = ''

    @property
    def time_sec(self):
        return (self.to_vertex.time - self.from_vertex.time).total_seconds()

    def has_same_points_and_type(self, other):
        return self.from_vertex == other.from_vertex and\
               self.to_vertex == other.to_vertex and\
               self.transport_type == other.transport_type

    @property
    def info(self):
        if self.route_name:
            return self.route_name
        if self.platform_code:
            return 'Perron ' + self.platform_code
        return ''

    def __lt__(self, other):
        return self.time < other.time_sec

    def __repr__(self):
        return '['+str(self.transport_type)+ ' ' + str(self.weather) + '] '+str(self.from_vertex)+' --> '+str(self.to_vertex)

