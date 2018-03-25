import datetime
from reisbrein.api import yoursapi
from reisbrein.api import openrouteserviceapi
from django.test import TestCase
from website.local_settings import *
from reisbrein.primitives import Location, TransportType
from reisbrein.generator.gen_common import FixTime
from ns_api import NSAPI
from .tomtom import TomTomApi
# from .mapquest import MapQuestApi
from .monotchapi import MonotchApi
from .weather import WeatherApi
from .rdwapi import RdwApi

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
        start = Location('Madurodam')
        end = Location('Martinitoren')
        travel1 = self.tomtom.travel_time(TomTomApi.RouteParams(start, end))[0]
        self.assertGreater(travel1, 2 * 3600)
        self.assertLess(travel1, 4 * 3600)

    def testAvoidHighway(self):
        start = Location('Madurodam')
        end = Location('Martinitoren')
        travel1 = self.tomtom.travel_time(TomTomApi.RouteParams(start, end, avoid_highways=True))[0]
        self.assertGreater(travel1, 8442)
        self.assertGreater(travel1, 4 * 3600)
        self.assertLess(travel1, 6 * 3600)

    def test_map_url(self):
        start = Location('Utrecht')
        end = Location('Amsterdam')
        url = self.tomtom.map_url(TomTomApi.RouteParams(start=start, end=end))
        self.assertEqual(url,'https://mydrive.tomtom.com/nl_nl/#mode=routes+routes={"departure":true,"traffic":true,"routeType":"FASTEST","travelMode":"CAR","points":["hw~52.09126,5.12275","hw~52.37317,4.89066"],"avoidCriteria":[]}+ver=3')


class TestYours(TestCase):

    def test_routing(self):
        start = Location('Madurodam')
        end = Location('Martinitoren')
        travel1 = yoursapi.travel_time(start.gps, end.gps, TransportType.CAR)
        # print(travel1)
        self.assertGreater(travel1, 2 * 3600)
        self.assertLess(travel1, 3 * 3600)
        travel2 = yoursapi.travel_time(start.gps, end.gps, TransportType.BIKE)
        # print(travel2)
        self.assertGreater(travel2, 10 * 3600)
        self.assertLess(travel2, 15 * 3600)
        # travel3 = yoursapi.travel_time(begin, end, TransportType.WALK)
        # print(travel3)
        # self.assertGreater(travel3, 10 * 3600)
        # self.assertLess(travel3, 15 * 3600)

    def test_map_url(self):
        start = Location('Madurodam')
        end = Location('Martinitoren')
        url = yoursapi.map_url(start, end, TransportType.CAR)
        # note that yournavigation.org DOES care about order: lat must come before lon
        self.assertEqual(url,'http://yournavigation.org/?flat=52.0993&flon=4.2986&tlat=53.21934&tlon=6.56817&v=motorcar&fast=1&layer=mapnik')
        url=url.replace('&', '?')
        words = sorted(url.split('?'))
        self.assertEqual(words, ['fast=1','flat=52.0993','flon=4.2986','http://yournavigation.org/','layer=mapnik','tlat=53.21934','tlon=6.56817','v=motorcar'])
        url = yoursapi.map_url(start, end, TransportType.BIKE)
        self.assertEqual(url,'http://yournavigation.org/?flat=52.0993&flon=4.2986&tlat=53.21934&tlon=6.56817&v=bicycle&fast=1&layer=mapnik')
        url=url.replace('&', '?')
        words = sorted(url.split('?'))
        self.assertEqual(words, ['fast=1','flat=52.0993','flon=4.2986','http://yournavigation.org/','layer=mapnik','tlat=53.21934','tlon=6.56817','v=bicycle'])
        url = yoursapi.map_url(start, end, TransportType.WALK)
        self.assertEqual(url,'http://yournavigation.org/?flat=52.0993&flon=4.2986&tlat=53.21934&tlon=6.56817&v=foot&fast=1&layer=mapnik')


class TestOpenRouteServiceApi(TestCase):

    def test_routing(self):
        start = Location('Madurodam')
        end = Location('Martinitoren')
        travel1, map_url = openrouteserviceapi.travel_time_and_map_url(start, end, TransportType.CAR)
        # print(travel1)
        self.assertGreater(travel1, 2 * 3600)
        self.assertLess(travel1, 3 * 3600)
        travel2, map_url = openrouteserviceapi.travel_time_and_map_url(start, end, TransportType.BIKE)
        # print(travel2)
        self.assertGreater(travel2, 10 * 3600)
        self.assertLess(travel2, 15 * 3600)
        # travel3 = yoursapi.travel_time(begin, end, TransportType.WALK)
        # print(travel3)
        # self.assertGreater(travel3, 10 * 3600)
        # self.assertLess(travel3, 15 * 3600)

    def test_map_url(self):
        start = Location('Madurodam')
        end = Location('Martinitoren')
        travel1, url = openrouteserviceapi.travel_time_and_map_url(start, end, TransportType.CAR)
        # note that yournavigation.org DOES care about order: lat must come before lon
        self.assertEqual(url, 'https://maps.openrouteservice.org/directions?n3=9&a=52.0993%2C4.2986%2C53.21934%2C6.56817&b=1a&c=0&g1=-1&g2=0&h2=3&k1=en-US&k2=km')
        travel1, url = openrouteserviceapi.travel_time_and_map_url(start, end, TransportType.BIKE)
        self.assertEqual(url, 'https://maps.openrouteservice.org/directions?n3=9&a=52.0993%2C4.2986%2C53.21934%2C6.56817&b=1a&c=0&g1=-1&g2=0&h2=3&k1=en-US&k2=km')
        travel1, url = openrouteserviceapi.travel_time_and_map_url(start, end, TransportType.WALK)
        self.assertEqual(url, 'https://maps.openrouteservice.org/directions?n3=9&a=52.0993%2C4.2986%2C53.21934%2C6.56817&b=1a&c=0&g1=-1&g2=0&h2=3&k1=en-US&k2=km')


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
        start_time = datetime.datetime.combine(datetime.date.today(), datetime.time(12))
        self.monotch.add_search_request(begin, end, start_time, FixTime.START)
        # print(result)
        # self.assertNotEqual(result, [])
        # self.assertEqual(len(result['itineraries']), 2)
        # self.assertEqual(len(result['itineraries'][0]['legs']), 5)
        # self.assertEqual(result['itineraries'][0]['legs'][3]['mode'], 'RAIL')
        # self.assertEqual(result['itineraries'][0]['legs'][3]['from']['name'], 'Den Haag Centraal')
        # dep_time_str = result['itineraries'][0]['legs'][3]['from']['departure']
        # dep_time = datetime.datetime.fromtimestamp(int(dep_time_str)/1000)
        # self.assertGreater(dep_time, start_time - datetime.timedelta(days=1))
        # self.assertLess(dep_time, start_time + datetime.timedelta(days=1))
        # self.assertEqual(result['itineraries'][0]['legs'][3]['to']['name'], 'Groningen')
        # arr_time_str = result['itineraries'][0]['legs'][3]['to']['arrival']
        # arr_time = datetime.datetime.fromtimestamp(int(arr_time_str)/1000)
        # self.assertGreater(arr_time, start_time - datetime.timedelta(days=1))
        # self.assertLess(arr_time, start_time + datetime.timedelta(days=1))


class TestRdw(TestCase):

    def setUp(self):
        self.rdw = RdwApi()

    def test_park_and_ride(self):
        parkings = self.rdw.get_park_and_rides()
        self.assertGreater(len(parkings), 10)
        parkings = self.rdw.get_park_and_rides()
        self.assertGreater(len(parkings), 10)
