from django.test import TestCase
from datetime import datetime
from reisbrein.planner import Point, Location
from reisbrein.generator.gen_walk import WalkGenerator
from reisbrein.segment import Segment, TransportType


class TestWalkGenerator(TestCase):

    def test(self):
        loc_utr = Location('Utrecht')
        loc_ams = Location('Amsterdam')
        noon = datetime(year=2017, month=11, day=17, hour=12)
        start = Point(location=loc_utr, time=noon)
        end = Point(location=loc_ams, time=noon)
        generator = WalkGenerator()
        segment = generator.create_segment(start, end)
        self.assertEqual(segment.transport_type, TransportType.WALK)
        self.assertEqual(segment.from_vertex.location, loc_utr)
        self.assertEqual(segment.from_vertex.time, noon)
        self.assertEqual(segment.to_vertex.location, loc_ams)
        self.assertEqual(segment.to_vertex.time, datetime(2017, 11, 17, 18, 2, 25, 755992))
