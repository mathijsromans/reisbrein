from django.test import TestCase
from datetime import datetime
from reisbrein.planner import Point, Location
from reisbrein.generator.gen_walk import WalkGenerator
from reisbrein.generator.gen_train import TrainGenerator, skip_first
from reisbrein.segment import Segment, TransportType


class TestWalkGenerator(TestCase):

    def test(self):
        loc_utr = Location('Utrecht')
        loc_ams = Location('Amsterdam')
        noon = datetime(year=2017, month=11, day=17, hour=12)
        start1 = Point(location=loc_utr, time=noon)
        end1 = Point(location=loc_ams, time=noon)
        start2 = Point(location=loc_utr, time=noon)
        end2 = Point(location=loc_ams, time=noon)
        generator = WalkGenerator()
        segment = generator.create_segment(start1, end1, WalkGenerator.FixTime.START)
        segment2 = generator.create_segment(start2, end2, WalkGenerator.FixTime.END)
        self.assertEqual(segment.transport_type, TransportType.WALK)
        self.assertEqual(segment.from_vertex.location, loc_utr)
        self.assertEqual(segment.to_vertex.location, loc_ams)
        self.assertEqual(segment.from_vertex.time, noon)
        self.assertEqual(segment.to_vertex.time, datetime(2017, 11, 17, 18, 2, 25, 755992))
        self.assertEqual(segment2.from_vertex.time, datetime(2017, 11, 17, 5, 57, 34, 244008))
        self.assertEqual(segment2.to_vertex.time, noon)


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


