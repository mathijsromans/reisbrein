import datetime
from reisbrein.api import yoursapi
from django.test import TestCase
from website.local_settings import *
from reisbrein.planner import Location
from ns_api import NSAPI
from .tomtom import TomTomApi
# from .mapquest import MapQuestApi
from .monotchapi import MonotchApi
from .weather import WeatherApi

import time

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

    def testSearch(self):
        location = self.tomtom.search('Madurodam')

    def testRouting(self):
        begin = Location('Madurodam')
        end = Location('Martinitoren')
        travel1 = self.tomtom.travel_time(begin, end)[0]
        # print(travel1)
        self.assertGreater(travel1, 2 * 3600)
        self.assertLess(travel1, 4 * 3600)


class TestYours(TestCase):

    def test_routing(self):
        begin = Location('Madurodam')
        end = Location('Martinitoren')
        travel1 = yoursapi.travel_time(begin, end, yoursapi.Mode.CAR)
        # print(travel1)
        self.assertGreater(travel1, 2 * 3600)
        self.assertLess(travel1, 3 * 3600)
        travel2 = yoursapi.travel_time(begin, end, yoursapi.Mode.BIKE)
        # print(travel2)
        self.assertGreater(travel2, 10 * 3600)
        self.assertLess(travel2, 15 * 3600)
        # travel3 = yoursapi.travel_time(begin, end, yoursapi.Mode.WALK)
        # print(travel3)
        # self.assertGreater(travel3, 10 * 3600)
        # self.assertLess(travel3, 15 * 3600)

    def test_map_url(self):
        begin = Location('Madurodam')
        end = Location('Martinitoren')
        url = yoursapi.map_url(begin, end, yoursapi.Mode.CAR)
        # note that yournavigation.org DOES care about order: lat must come before lon
        self.assertEqual(url,'http://yournavigation.org/?flat=52.0993&flon=4.2986&tlat=53.21934&tlon=6.56817&v=motorcar&fast=1&layer=mapnik')
        url=url.replace('&', '?')
        words = sorted(url.split('?'))
        self.assertEqual(words, ['fast=1','flat=52.0993','flon=4.2986','http://yournavigation.org/','layer=mapnik','tlat=53.21934','tlon=6.56817','v=motorcar'])
        url = yoursapi.map_url(begin, end, yoursapi.Mode.BIKE)
        self.assertEqual(url,'http://yournavigation.org/?flat=52.0993&flon=4.2986&tlat=53.21934&tlon=6.56817&v=bicycle&fast=1&layer=mapnik')
        url=url.replace('&', '?')
        words = sorted(url.split('?'))
        self.assertEqual(words, ['fast=1','flat=52.0993','flon=4.2986','http://yournavigation.org/','layer=mapnik','tlat=53.21934','tlon=6.56817','v=bicycle'])


# class TestMapQuest(TestCase):
#
#     def setUp(self):
#         self.mapquest = MapQuestApi()
#
#     def testSearch(self):
#         location = self.mapquest.search('wassenaarsseweg 220 Den Haag')
#         location = self.mapquest.search('wassenaarsseweg 220 Den Haag')


class TestWeather(TestCase):

    def setUp(self):
        self.weather = WeatherApi()

    def testSearch(self):
        weather = self.weather.search('Madrid')
        # print(weather)

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
        self.assertEqual(len(result['itineraries']), 1)
        self.assertEqual(len(result['itineraries'][0]['legs']), 8)
        self.assertEqual(result['itineraries'][0]['legs'][3]['mode'], 'RAIL')
        self.assertEqual(result['itineraries'][0]['legs'][3]['from']['name'], 'Den Haag Centraal')
        dep_time_str = result['itineraries'][0]['legs'][3]['from']['departure']
        dep_time = datetime.datetime.fromtimestamp(int(dep_time_str)/1000)
        self.assertGreater(dep_time, datetime.datetime(year=2017, month=11, day=16))
        self.assertLess(dep_time, datetime.datetime(year=2017, month=11, day=30))
        self.assertEqual(result['itineraries'][0]['legs'][3]['to']['name'], 'Amersfoort')
        arr_time_str = result['itineraries'][0]['legs'][3]['to']['arrival']
        arr_time = datetime.datetime.fromtimestamp(int(arr_time_str)/1000)
        self.assertGreater(arr_time, datetime.datetime(year=2017, month=11, day=16))
        self.assertLess(arr_time, datetime.datetime(year=2017, month=11, day=30))
