from datetime import datetime, timedelta
from django.test import TestCase
from .graph import Graph, shortest_path, Edge
from .planner import Planner, Plan, VehiclePositions
from reisbrein.generator.gen_common import FixTime, get_locations
from .views import PlanView
from reisbrein.primitives import Location, Point, TransportType, Segment, noon_today, VehicleType, Vehicle
from .userpreference import order_and_select
from .models import UserTravelPreferences


class TestTest(TestCase):
    """ Example test case. """

    def test_asserts(self):
        """ Example unit test. Tests unittest asserts. """
        self.assertTrue(True)
        self.assertEqual(True, True)
        self.assertNotEqual(True, False)


class TestPrimitives(TestCase):
    """ Example test case. """

    def test_points(self):
        # location and point are value classes
        l1 = Location('a', (2,3))
        l2 = Location('a', (2,3))
        l3 = Location('b', (2,3))
        l4 = Location('a', (3,3))
        t0 = datetime(year=2000, month=1, day=1)
        t1 = t0 + timedelta(seconds=60)
        p1 = Point(l1, t0)
        p2 = Point(l2, t0)
        p3 = Point(l3, t0)
        p4 = Point(l4, t0)
        p5 = Point(l1, t1)
        p6 = Point(l2, t1)

        self.assertFalse(l1 is l2)
        self.assertTrue(l1 == l2)
        self.assertFalse(p1 is p2)
        self.assertTrue(p1 == p2)
        self.assertFalse(l1 == l3)
        self.assertFalse(l1 == l4)
        self.assertFalse(p1 == p3)
        self.assertFalse(p1 == p4)
        self.assertTrue(p1.location == p5.location)
        self.assertTrue(p2.location == p6.location)
        self.assertFalse(p1 == p5)
        self.assertFalse(p2 == p6)

        ll = [l1, l3]
        lp = [p1, p3]

        self.assertTrue(l1 in ll)
        self.assertTrue(l2 in ll)
        self.assertTrue(l3 in ll)
        self.assertFalse(l4 in ll)
        self.assertTrue(p1 in lp)
        self.assertTrue(p2 in lp)
        self.assertTrue(p3 in lp)
        self.assertFalse(p4 in lp)

        sl = set([l1, l2, l3, l4])
        sp = set([p1, p2, p3, p4, p5, p6])

        self.assertEqual(len(sl), 3)
        self.assertEqual(len(sp), 4)

        self.assertTrue(Location('a', (2,3)) in sl)
        self.assertTrue(Point(l1, t0) in sp)
        self.assertFalse(Location('b', (3,3)) in sl)
        self.assertFalse(Point(l3, t1) in sp)


class TestGraph(TestCase):

    def test(self):
        G = Graph()
        G.add_vertex('a')
        G.add_vertex('b')
        G.add_vertex('c')
        G.add_vertex('d')
        G.add_vertex('e')

        G.add_edge(Edge('a', 'b', 2))
        G.add_edge(Edge('a', 'c', 8))
        G.add_edge(Edge('a', 'd', 5))
        G.add_edge(Edge('b', 'c', 1))
        G.add_edge(Edge('c', 'e', 3))
        G.add_edge(Edge('d', 'e', 4))

        vertices = [edge.to_vertex for edge in shortest_path(G, 'a', 'e')]
        self.assertEqual(vertices, ['b', 'c', 'e'])


class TestLocation(TestCase):

    def test_basic(self):
        loc = Location('Utrecht')
        self.assertEqual(loc.gps, (52.09126, 5.12275))
        loc2 = Location('ddd-unknown-location-ddsfaasdfasdf')
        self.assertEqual(loc2.gps, None)

    def test_mid(self):
        loc1 = Location('a', (0.5, 1.5))
        loc2 = Location('b', (1.5, 3.5))

        mid1 = Location.midpoint(loc1, loc2)
        self.assertEqual(mid1.loc_str, 'mid_a_b')
        self.assertEqual(mid1.gps, (1.0, 2.5))

        mid2 = Location.midpoint(loc1, loc2, 0.75)
        self.assertEqual(mid2.loc_str, 'mid_a_b')
        self.assertEqual(mid2.gps, (1.25, 3.0))


class TestViewSimple(TestCase):

    def setUp(self):
        self.planner = Planner()

    def test(self):
        noon = noon_today()
        plans = self.planner.solve(Location('Den Haag'), Location('Nieuwegein'), noon, FixTime.START)
        results = PlanView.get_results(plans)
        # for p in plans:
        #     print (list(map(str,p)))
        self.assertGreater(len(plans), 2)
        self.assertGreater(results[0]['travel_time_min'], 20)
        self.assertLess(results[0]['travel_time_min'], 120)
        for p in plans:
            for s in p.route:
                if s.transport_type in (TransportType.BIKE, TransportType.CAR):
                    self.assertNotEqual(s.map_url, '')


class TestViewExtra(TestCase):

    def setUp(self):
        self.planner = Planner()


    def test_no_short_bike_rides(self):
        noon = noon_today()
        plans = self.planner.solve(Location('Centraal Museum'), Location('Oldambt utrecht'), noon, FixTime.START)
        for p in plans:
            for s in p.route:
                if s.transport_type in (TransportType.BIKE, TransportType.OVFIETS):
                    self.assertGreater(s.to_vertex.time-s.from_vertex.time, timedelta(minutes=1, seconds=55))

    def test_doubles(self):
        noon = noon_today()
        plans = self.planner.solve(Location('Den haag centraal'), Location('Utrecht centraal'), noon, FixTime.START)
        segments = set()
        for p in plans:
            segments.update(p.route)
        for s1 in segments:
            for s2 in segments:
                if not s1 is s2:
                    self.assertFalse(s1.from_vertex == s2.from_vertex and
                                     s1.to_vertex == s2.to_vertex and
                                     s1.transport_type == s2.transport_type)


class TestUserPreference(TestCase):

    @staticmethod
    def create_plan(segments):

        # litter the place with OV-fietsen and cars
        vehicle_positions = VehiclePositions()
        for location in get_locations(segments):
            vehicle_positions.add_vehicle(location, Vehicle(TransportType.BIKE, VehicleType.OVFIETS))
            vehicle_positions.add_vehicle(location, Vehicle(TransportType.CAR, VehicleType.CAR))

        p = Plan(vehicle_positions)
        for s in segments:
            assert p.add_segment(s)
        return p

    def get_plans(self):
        t0 = datetime(year=2000, month=1, day=1)
        points = {
            'a':  Point('a', t0),
            'z1': Point('z', t0 + timedelta(hours=3)),
            'z2': Point('z', t0 + timedelta(hours=3, minutes=1)),
            'c':  Point('c', t0 + timedelta(hours=2)),
            'z3': Point('z', t0 + timedelta(hours=5)),
            'a2': Point('a', t0 + timedelta(hours=12)),
            'c2': Point('c', t0 + timedelta(hours=13)),
            'z4': Point('z', t0 + timedelta(hours=14)),
            'z5': Point('z', t0 + timedelta(hours=6)),
            'z6': Point('z', t0 + timedelta(hours=2, minutes=59)),
        }
        carplan = self.create_plan(
            [
                Segment(TransportType.CAR, points['a'], points['z1']),
            ]
        )
        bikeplan = self.create_plan(
            [
                Segment(TransportType.BIKE, points['a'], points['z2']),
            ]
        )
        publicplan1 = self.create_plan(
            [
                Segment(TransportType.WALK, points['a'], points['c']),
                Segment(TransportType.TRAIN, points['c'], points['z3']),
            ]
        )
        publicplan2 = self.create_plan(
            [
                Segment(TransportType.WAIT, points['a'], points['a2']),
                Segment(TransportType.WALK, points['a2'], points['c2']),
                Segment(TransportType.TRAIN, points['c2'], points['z4']),
            ]
        )
        walkplan = self.create_plan(
            [
                Segment(TransportType.WALK, points['a'], points['z5']),
            ]
        )
        bikeplan2 = self.create_plan(
            [
                Segment(TransportType.BIKE, points['a'], points['z6']),
            ]
        )
        return bikeplan, carplan, publicplan1, publicplan2, walkplan, bikeplan2

    def test_simple(self):
        bikeplan, carplan, publicplan1, publicplan2, walkplan, bikeplan2 = self.get_plans()
        plans = [bikeplan, carplan, publicplan1]
        order_and_select(plans, UserTravelPreferences(), None)
        self.assertEqual(plans, [bikeplan, carplan, publicplan1])

        # quick biking is better than long walking
        plans = [walkplan, bikeplan]
        # print(str(bikeplan) + ' has a2 score ' + str(bikeplan.score))
        order_and_select(plans, UserTravelPreferences(), None)
        self.assertEqual(plans, [bikeplan, walkplan])


    def test_short_plans(self):
        # publicplan2 is too long
        bikeplan, carplan, publicplan1, publicplan2, walkplan, bikeplan2 = self.get_plans()
        plans = [bikeplan, carplan, publicplan1, publicplan2]
        order_and_select(plans, UserTravelPreferences(), None)
        self.assertEqual(plans, [bikeplan, carplan, publicplan1])

        # not enough plans, so keep publicplan2
        plans = [publicplan2, carplan, publicplan1]
        order_and_select(plans, UserTravelPreferences(), FixTime.START)
        self.assertEqual(plans, [carplan, publicplan1, publicplan2])

    def test_bike_preference(self):
        bikeplan, carplan, publicplan1, publicplan2, walkplan, bikeplan2 = self.get_plans()
        prefs = UserTravelPreferences()
        self.assertEqual(prefs.likes_to_bike, 5)
        plans = [bikeplan, carplan]
        order_and_select(plans, prefs, None)
        self.assertEqual(plans, [bikeplan, carplan])
        prefs.likes_to_bike = 6
        plans = [bikeplan, carplan]
        order_and_select(plans, prefs, None)
        self.assertEqual(plans, [bikeplan, carplan])
        prefs.likes_to_bike = 3
        plans = [bikeplan2, carplan]
        order_and_select(plans, prefs, None)
        self.assertEqual(plans, [bikeplan2, carplan])
        prefs.likes_to_bike = 2
        plans = [bikeplan2, carplan]
        order_and_select(plans, prefs, None)
        self.assertEqual(plans, [carplan, bikeplan2])




