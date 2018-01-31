from django.test import TestCase
from datetime import datetime, timedelta
from reisbrein.generator.gen_walk import WalkGenerator
from reisbrein.generator.gen_public import PublicGenerator, MockPublicGenerator
from reisbrein.generator.gen_train import TrainGenerator, skip_first
from reisbrein.generator.gen_car import CarGenerator
from reisbrein.generator.gen_parkride import ParkRideGenerator
from reisbrein.primitives import TransportType, Point, Location, noon_today
from .gen_common import FixTime
from reisbrein.api.monotchapi import MonotchApi


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
        self.assertEqual(new_point.time, datetime(2017, 11, 17, 22, 3, 38, 86834))
        self.assertEqual(new_point2.time, datetime(2017, 11, 17, 1, 56, 21, 913166))
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

        loc_bhd  = Location('sloterweg 183, badhoevedorp', (52.33668,4.77682))
        loc_mee = Location('Station Meerssen', (51.1923957995,5.99421143532))
        start = Point(location=loc_bhd, time=noon)
        end = Point(location=loc_mee, time=noon)
        segment, new_point = generator.create_segment(start, end, FixTime.START, TransportType.BIKE)
        self.assertEqual(segment.transport_type, TransportType.BIKE)
        self.assertEqual(segment.from_vertex.location, loc_bhd)
        self.assertEqual(segment.to_vertex.location, loc_mee)
        self.assertGreater(segment.to_vertex.time - segment.from_vertex.time, timedelta(hours=4))
        self.assertLess(segment.to_vertex.time - segment.from_vertex.time, timedelta(hours=14))

        loc_bhd  = Location('parkzichtlaan', (52.10073, 5.03322))
        loc_mee = Location('Utrecht Centraal', (52.089820488, 5.10957062244))
        start = Point(location=loc_bhd, time=noon)
        end = Point(location=loc_mee, time=noon)
        segment, new_point = generator.create_segment(start, end, FixTime.START, TransportType.BIKE)
        self.assertEqual(segment.transport_type, TransportType.BIKE)
        self.assertEqual(segment.from_vertex.location, loc_bhd)
        self.assertEqual(segment.to_vertex.location, loc_mee)
        self.assertGreater(segment.to_vertex.time - segment.from_vertex.time, timedelta(minutes=10))
        self.assertLess(segment.to_vertex.time - segment.from_vertex.time, timedelta(minutes=30))


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
        self.assertIsNotNone(location.gps)
        closest = [station.naam for station in self.generator.closest_stations(location, 3)]
        expected = ['Den Haag Centraal', 'Den Haag HS', 'Den Haag Laan v NOI']
        self.assertEqual(closest, expected)

    def test(self):
        noon = noon_today()
        start = Point(Location('Madurodam'), noon)
        end = Point(Location('Martinitoren'), noon)
        segments = []
        self.generator.create_edges(start, end, FixTime.START, segments)
        self.assertEqual(len(segments), 4)


def gen_points(req_time, fix_time):
    start_time = req_time if fix_time == FixTime.START else req_time-timedelta(hours=10)
    end_time   = req_time if fix_time == FixTime.END else req_time+timedelta(hours=10)
    start = Point(Location('Den Haag'), start_time)
    end = Point(Location('Nieuwegein'), end_time)
    return start, end


def gen_edges(start, end, fix_time, generator):
    edges = []
    request = generator.prepare_request(start, end, fix_time)
    generator.do_requests()
    request.finish(edges)
    return edges


class TestPublicGenerator(TestCase):

    def setUp(self):
        self.noon = noon_today()
        routing_api = MonotchApi()
        self.public_generator = PublicGenerator(routing_api)

    def test_fixed_time_start(self):
        fix_time = FixTime.START
        start, end = gen_points(self.noon, fix_time)
        edges = gen_edges(start, end, fix_time, self.public_generator)
        for e in edges:
            # print(e)
            if e.transport_type != TransportType.WAIT:
                self.assertGreaterEqual(e.from_vertex.time, self.noon)
                self.assertLess(e.from_vertex.time, self.noon + timedelta(hours=2))
                self.assertGreaterEqual(e.to_vertex.time, self.noon)
                self.assertLess(e.to_vertex.time, self.noon + timedelta(hours=2))
        self.assertGreater(len(edges), 8)

    def test_fixed_time_end(self):
        fix_time = FixTime.END
        start, end = gen_points(self.noon, fix_time)
        edges = gen_edges(start, end, fix_time, self.public_generator)
        for e in edges:
            # print(e)
            if e.transport_type != TransportType.WAIT:
                self.assertLessEqual(e.from_vertex.time, self.noon)
                self.assertGreater(e.from_vertex.time, self.noon - timedelta(hours=2))
                self.assertLessEqual(e.to_vertex.time, self.noon)
                self.assertGreater(e.to_vertex.time, self.noon - timedelta(hours=2))
        self.assertGreater(len(edges), 8)

    def test_mocking(self):
        fix_time = FixTime.START
        start, end = gen_points(self.noon, fix_time)
        edges = gen_edges(start, end, fix_time, MockPublicGenerator())
        for e in edges:
            # print(e)
            if e.transport_type != TransportType.WAIT:
                self.assertGreaterEqual(e.from_vertex.time, self.noon)
                self.assertLess(e.from_vertex.time, self.noon + timedelta(hours=2))
                self.assertGreaterEqual(e.to_vertex.time, self.noon)
                self.assertLess(e.to_vertex.time, self.noon + timedelta(hours=2))
        fix_time = FixTime.END
        start, end = gen_points(self.noon, fix_time)
        edges = gen_edges(start, end, fix_time, MockPublicGenerator())
        for e in edges:
            # print(e)
            if e.transport_type != TransportType.WAIT:
                self.assertLessEqual(e.from_vertex.time, self.noon)
                self.assertGreater(e.from_vertex.time, self.noon - timedelta(hours=2))
                self.assertLessEqual(e.to_vertex.time, self.noon)
                self.assertGreater(e.to_vertex.time, self.noon - timedelta(hours=2))


class TestParkRideGenerator(TestCase):

    def setUp(self):
        self.public_generator = MockPublicGenerator()
        self.park_ride_generator = ParkRideGenerator(self.public_generator)
        self.car_generator = CarGenerator()
        self.noon = noon_today()

    def test_fixed_time_start(self):
        fix_time = FixTime.START
        start, end = gen_points(self.noon, fix_time)
        edges = gen_edges(start, end, fix_time, self.park_ride_generator)
        self.car_generator.create_edges(start, end, fix_time, edges)
        for e in edges:
            # print(e)
            if e.transport_type != TransportType.WAIT:
                self.assertGreaterEqual(e.from_vertex.time, self.noon)
                self.assertLess(e.from_vertex.time, self.noon + timedelta(hours=2))
                self.assertGreaterEqual(e.to_vertex.time, self.noon)
                self.assertLess(e.to_vertex.time, self.noon + timedelta(hours=2))
        self.assertEqual(len(edges), 14)

    def test_fixed_time_end(self):
        fix_time = FixTime.END
        start, end = gen_points(self.noon, fix_time)
        edges = gen_edges(start, end, fix_time, self.park_ride_generator)
        self.car_generator.create_edges(start, end, fix_time, edges)
        for e in edges:
            # print(e)
            if e.transport_type != TransportType.WAIT:
                self.assertLessEqual(e.from_vertex.time, self.noon)
                self.assertGreater(e.from_vertex.time, self.noon - timedelta(hours=2))
                self.assertLessEqual(e.to_vertex.time, self.noon)
                self.assertGreater(e.to_vertex.time, self.noon - timedelta(hours=2))
        self.assertEqual(len(edges), 14)

