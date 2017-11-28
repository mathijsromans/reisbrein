from datetime import datetime, timedelta
from django.test import TestCase
from .graph import Graph, shortest_path, Edge
from .planner import Planner, DijkstraRouter, recur_map, Plan
from reisbrein.generator.generator import TestGenerator
from .views import PlanView
from reisbrein.primitives import Location, Point, TransportType, Segment, noon_today
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

    def test(self):
        loc = Location('Utrecht')
        self.assertEqual(loc.gps(), (52.09126, 5.12275))
        loc2 = Location('ddd-unknown-location-ddsfaasdfasdf')
        self.assertEqual(loc2.gps(), None)


class TestDijkstraRouter(TestCase):

    def test_fixed_generator(self):
        p = Planner(TestGenerator, DijkstraRouter)

        vertices = []
        noon = noon_today()
        for plan in p.solve('a', 'e', noon):
            vertices.append([edge.to_vertex for edge in plan.route])

        # [['b', 'c', <reisbrein.planner.Point object at 0x7f8eee966630>],
        #  [<reisbrein.planner.Point object at 0x7f8eee966630>],
        #  [<reisbrein.planner.Point object at 0x7f8eee966630>]]

        # self.assertEqual(len(vertices), 3)
        # self.assertEqual(len(vertices[0]), 3)
        # self.assertEqual(vertices[0][0], 'b')
        # self.assertEqual(vertices[0][1], 'c')
        # self.assertEqual(vertices[0][2].location.loc_str, 'e')

    def test_planner(self):
        p = Planner(router=DijkstraRouter)
        vertices = []
        noon = noon_today()
        for plan in p.solve('Madurodam', 'Martinitoren', noon):
            vertices.append([edge.to_vertex for edge in plan.route])

        # print(list(recur_map(str, vertices)))
        # [['Station: Den Haag HS @ 2017-11-17 12:10:00', 'Station: Groningen Noord @ 2017-11-17 12:40:00',
        # 'Martinitoren @ 2017-11-17 12:50:00'], ['Station: Den Haag HS @ 2017-11-17 12:10:00',
        # 'Station: Groningen Noord @ 2017-11-17 12:40:00', 'Martinitoren @ 2017-11-17 12:50:00'], []]

        # self.assertEqual(len(vertices), 2)
        # self.assertEqual(len(vertices[0]), 1)
        # self.assertEqual(len(vertices[1]), 1)
        # self.assertEqual(len(vertices[2]), 1)


class TestRichRouter(TestCase):

    def test_fixed_generator(self):
        p = Planner(generator=TestGenerator)

        vertices = []
        noon = noon_today()
        plans = p.solve('a', 'e', noon)
        for plan in plans:
            vertices.append([edge.to_vertex for edge in plan.route])
        # print(list(recur_map(str, plans)))

        # self.assertEqual(len(plans), 4)
        # self.assertEqual(len(plans[0]), 3)
        # self.assertEqual(len(plans[1]), 2)

    def test_planner(self):
        p = Planner()
        vertices = []
        noon = noon_today()
        plans = p.solve('Madurodam', 'Martinitoren', noon)
        for plan in plans:
            vertices.append([edge.to_vertex for edge in plan.route])
        # print(list(recur_map(str, vertices)))

        # self.assertEqual(len(plans), 4)
        # self.assertEqual(len(plans[0]), 4)
        # self.assertEqual(len(plans[1]), 4)


class TestViews(TestCase):

    def setUp(self):
        self.planner = Planner()

    def test(self):
        time = noon_today()
        plans = self.planner.solve('Den Haag', 'Nieuwegein', time)
        results = PlanView.get_results(plans)
        # for p in plans:
        #     print (list(map(str,p)))
        self.assertGreater(len(plans), 2)
        self.assertGreater(results[0]['travel_time_min'], 20)
        self.assertLess(results[0]['travel_time_min'], 120)
        for p in plans:
            for s in p.route:
                if s.transport_type == TransportType.BIKE:
                    self.assertNotEqual(s.map_url, '')

    def test_no_short_bike_rides(self):
        time = noon_today()
        plans = self.planner.solve('Centraal Museum', 'Oldambt utrecht', time)
        for p in plans:
            for s in p.route:
                if s.transport_type in (TransportType.BIKE, TransportType.OVFIETS):
                    self.assertGreater(s.to_vertex.time-s.from_vertex.time, timedelta(minutes=1, seconds=55))

    def test_doubles(self):
        time = noon_today()
        plans = self.planner.solve('Den haag centraal', 'Utrecht centraal', time)
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
        carplan = Plan(
            [
                Segment(TransportType.CAR, points['a'], points['z1']),
            ]
        )
        bikeplan = Plan(
            [
                Segment(TransportType.BIKE, points['a'], points['z2']),
            ]
        )
        publicplan1 = Plan(
            [
                Segment(TransportType.WALK, points['a'], points['c']),
                Segment(TransportType.TRAIN, points['c'], points['z3']),
            ]
        )
        publicplan2 = Plan(
            [
                Segment(TransportType.WAIT, points['a'], points['a2']),
                Segment(TransportType.WALK, points['a2'], points['c2']),
                Segment(TransportType.TRAIN, points['c2'], points['z4']),
            ]
        )
        walkplan = Plan(
            [
                Segment(TransportType.WALK, points['a'], points['z5']),
            ]
        )
        bikeplan2 = Plan(
            [
                Segment(TransportType.BIKE, points['a'], points['z6']),
            ]
        )
        return bikeplan, carplan, publicplan1, publicplan2, walkplan, bikeplan2

    def test_simple(self):
        bikeplan, carplan, publicplan1, publicplan2, walkplan, bikeplan2 = self.get_plans()
        plans = [bikeplan, carplan, publicplan1]
        order_and_select(plans, UserTravelPreferences())
        self.assertEqual(plans, [carplan, bikeplan, publicplan1])

        # quick biking is better than long walking
        plans = [walkplan, bikeplan]
        # print(str(bikeplan) + ' has a2 score ' + str(bikeplan.score))
        order_and_select(plans, UserTravelPreferences())
        self.assertEqual(plans, [bikeplan, walkplan])


    def test_short_plans(self):
        # publicplan2 is too long
        bikeplan, carplan, publicplan1, publicplan2, walkplan, bikeplan2 = self.get_plans()
        plans = [bikeplan, carplan, publicplan1, publicplan2]
        order_and_select(plans, UserTravelPreferences())
        self.assertEqual(plans, [carplan, bikeplan, publicplan1])

        # not enough plans, so keep publicplan2
        plans = [publicplan2, carplan, publicplan1]
        order_and_select(plans, UserTravelPreferences())
        self.assertEqual(plans, [carplan, publicplan1, publicplan2])

    def test_bike_preference(self):
        bikeplan, carplan, publicplan1, publicplan2, walkplan, bikeplan2 = self.get_plans()
        prefs = UserTravelPreferences()
        self.assertEqual(prefs.likes_to_bike,5)
        plans = [bikeplan, carplan]
        order_and_select(plans, prefs)
        self.assertEqual(plans, [carplan, bikeplan])
        prefs.likes_to_bike=6
        plans = [bikeplan, carplan]
        order_and_select(plans, prefs)
        self.assertEqual(plans, [bikeplan, carplan])
        prefs.likes_to_bike=5
        plans = [bikeplan2, carplan]
        order_and_select(plans, prefs)
        self.assertEqual(plans, [bikeplan2, carplan])
        prefs.likes_to_bike=4
        plans = [bikeplan2, carplan]
        order_and_select(plans, prefs)
        self.assertEqual(plans, [carplan, bikeplan2])




