from django.test import TestCase
from website.local_settings import *
from reisbrein.planner import Location
from ns_api import *
from .tomtom import TomTomApi
from .monotchapi import MonotchApi


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
        self.assertGreater(self.tomtom.travel_time( begin, end ), 8000)


class TestMonotch(TestCase):

    def setUp(self):
        self.monotch = MonotchApi()

    def testStations(self):
        begin = Location('Madurodam')
        end = Location('Martinitoren')
        result = self.monotch.search(begin, end)
        # print(result)
        self.assertNotEqual(result, [])
        self.assertEqual(len(result['itineraries']), 6)
        self.assertEqual(len(result['itineraries'][0]['legs']), 5)
        # self.assertEqual(len(result['itineraries'][0]['legs']['from']), 5)
        # self.assertEqual(len(result['itineraries'][0]['legs']['from']), 5)