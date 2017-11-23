from django.test import TestCase
from datetime import datetime, timedelta
from reisbrein.generator.gen_walk import WalkGenerator
from reisbrein.generator.gen_public import PublicGenerator
from reisbrein.generator.gen_train import TrainGenerator, skip_first
from reisbrein.primitives import TransportType, Point, Location
from .gen_common import FixTime
from reisbrein.planner import recur_map


class TestWalkGenerator(TestCase):

    def test(self):
        loc_utr = Location('Utrecht, Centraal')
        loc_ams = Location('Amsterdam, Centraal')
        noon = datetime(year=2017, month=11, day=17, hour=12)
        start1 = Point(location=loc_utr, time=noon)
        end1 = Point(location=loc_ams, time=noon)
        start2 = Point(location=loc_utr, time=noon)
        end2 = Point(location=loc_ams, time=noon)
        generator = WalkGenerator()
        segment, new_point = generator.create_segment(start1, end1, FixTime.START, TransportType.WALK)
        segment2, new_point2 = generator.create_segment(start2, end2, FixTime.END, TransportType.WALK)
        self.assertEqual(segment.transport_type, TransportType.WALK)
        self.assertEqual(segment.from_vertex.location, loc_utr)
        self.assertEqual(segment.to_vertex.location, loc_ams)
        self.assertEqual(segment.from_vertex.time, noon)
        self.assertEqual(new_point.time, datetime(2017, 11, 17, 17, 52, 7, 217320))
        self.assertEqual(new_point2.time, datetime(2017, 11, 17, 6, 7, 52, 782680))
        self.assertEqual(segment2.to_vertex.time, noon)

        segment, new_point = generator.create_segment(start1, end1, FixTime.START, TransportType.BIKE)
        segment2, new_point2 = generator.create_segment(start2, end2, FixTime.END, TransportType.BIKE)
        self.assertEqual(segment.transport_type, TransportType.BIKE)
        self.assertEqual(segment.from_vertex.location, loc_utr)
        self.assertEqual(segment.to_vertex.location, loc_ams)
        self.assertEqual(segment.from_vertex.time, noon)
        self.assertAlmostEqual(new_point.time, datetime(2017, 11, 17, 14, 2, 3), delta=timedelta(seconds=600))
        self.assertAlmostEqual(new_point2.time, datetime(2017, 11, 17, 9, 57, 57), delta=timedelta(seconds=600))
        self.assertEqual(segment2.to_vertex.time, noon)

        edges = [segment, segment2]
        generator.add_weather(edges)
        # print(segment)
        # print(segment2)


class TestTrainGenerator(TestCase):

    def setUp(self):
        self.generator = TrainGenerator()

    def test_skip(self):
        result = []
        for i in skip_first(range(0,5)):
            result.append(i)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_closest_stations(self):
        location = Location('Madurodam')
        self.assertIsNotNone(location.gps())
        closest = [station.naam for station in self.generator.closest_stations(location, 3)]
        expected = ['Den Haag Centraal', 'Den Haag HS', 'Den Haag Laan v NOI']
        self.assertEqual(closest, expected)

    def test(self):
        noon = datetime(year=2017, month=11, day=17, hour=12)
        start = Point(Location('Madurodam'), noon)
        end = Point(Location('Martinitoren'), noon)
        segments = []
        self.generator.create_edges(start, end, segments)
        self.assertEqual(len(segments), 4)


class TestPublicGenerator(TestCase):
    def setUp(self):
        self.generator = PublicGenerator()

    def test(self):
        time = datetime(year=2017, month=11, day=18, hour=9)
        start = Point(Location('Den Haag'), time)
        end = Point(Location('Nieuwegein'), time)
        segments = []
        self.generator.create_edges(start, end, segments)
        # for s in segments:
        #     print(s)
        self.assertEqual(len(segments), 12)

