from django.test import TestCase
import datetime
from website.local_settings import *
from reisbrein.planner import Location
from ns_api import NSAPI
from .tomtom import TomTomApi
from .mapquest import MapQuestApi
from .monotchapi import MonotchApi
import time

class TestNSAPI(TestCase):

    def setUp(self):
        self.nsapi = NSAPI(NSAPI_USERNAME, NSAPI_KEY)

    def testStations(self):
        if NSAPI_USERNAME:
            stations = self.nsapi.get_stations()
            self.assertGreater(len(stations), 10)


# class TestTomTom(TestCase):
#
#     def setUp(self):
#         self.tomtom = TomTomApi()
#
#     def testSearch(self):
#         location = self.tomtom.search('Madurodam')
#
#     def testStations(self):
#         begin = Location('Madurodam')
#         end = Location('Martinitoren')
#         self.assertGreater(self.tomtom.travel_time( begin, end ), 8000)

class TestMapQuest(TestCase):

    def setUp(self):
        self.mapquest = MapQuestApi()

    def testSearch(self):
        location = self.mapquest.search('wassenaarsseweg 220 Den Haag')
        location = self.mapquest.search('wassenaarsseweg 220 Den Haag')

class TestMonotch(TestCase):

    def setUp(self):
        self.monotch = MonotchApi()

    def testStations(self):
        begin = Location('Madurodam')
        end = Location('Martinitoren')
        start_time = datetime.datetime(year=2017, month=11, day=17, hour=22, minute=20)
        result = self.monotch.search(begin, end, start_time)
        # print(result)
        self.assertNotEqual(result, [])
        self.assertEqual(len(result['itineraries']), 2)
        self.assertEqual(len(result['itineraries'][0]['legs']), 5)
        self.assertEqual(result['itineraries'][0]['legs'][3]['mode'], 'RAIL')
        self.assertEqual(result['itineraries'][0]['legs'][3]['from']['name'], 'Den Haag Centraal')
        dep_time_str = result['itineraries'][0]['legs'][3]['from']['departure']
        dep_time = datetime.datetime.fromtimestamp(int(dep_time_str)/1000)
        self.assertGreater(dep_time, datetime.datetime(year=2017, month=11, day=16))
        self.assertLess(dep_time, datetime.datetime(year=2017, month=11, day=30))
        self.assertEqual(result['itineraries'][0]['legs'][3]['to']['name'], 'Groningen')
        arr_time_str = result['itineraries'][0]['legs'][3]['to']['arrival']
        arr_time = datetime.datetime.fromtimestamp(int(arr_time_str)/1000)
        self.assertGreater(arr_time, datetime.datetime(year=2017, month=11, day=16))
        self.assertLess(arr_time, datetime.datetime(year=2017, month=11, day=30))
