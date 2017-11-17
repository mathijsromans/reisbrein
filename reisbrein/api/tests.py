from django.test import TestCase
from website.local_settings import *
from reisbrein.planner import Location
from ns_api import *
from .tomtom import TomTomApi


class TestNSAPI(TestCase):

    def setUp(self):
        self.nsapi = NSAPI(NSAPI_USERNAME, NSAPI_KEY)

    def testStations(self):
        if NSAPI_USERNAME:
            stations = self.nsapi.get_stations()
            self.assertGreater(len(stations), 10)


class TestTomTom(TestCase):

    def setUp(self):
        self.tomtom = TomTomApi()

    def testStations(self):
        begin = Location('Madurodam')
        end = Location('Martinitoren')
        self.assertGreater(self.tomtom.travel_time( begin, end ), 8300)