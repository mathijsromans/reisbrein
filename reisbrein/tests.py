from datetime import datetime
from django.test import TestCase
from .graph import Graph, shortest_path, Edge
from .planner import Planner, Location, Point
from reisbrein.generator.generator import TestGenerator, Generator
from .views import PlanView


def recur_map(f, data):
    return [not hasattr(x, "__iter__") and f(x) or recur_map(f, x) for x in data]


class TestTest(TestCase):
    """ Example test case. """

    def test_asserts(self):
        """ Example unit test. Tests unittest asserts. """
        self.assertTrue(True)
        self.assertEqual(True, True)
        self.assertNotEqual(True, False)


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
        self.assertEqual(loc.gps(), (52.08095165, 5.12768031549829))
        loc2 = Location('ddd-unknown-location-ddsfaasdfasdf')
        self.assertEqual(loc2.gps(), None)


class TestPlanner(TestCase):

    def test_fixed_generator(self):
        p = Planner(TestGenerator())

        vertices = []
        noon = datetime(year=2017, month=11, day=17, hour=12)
        for plan in p.solve('a', 'e', noon):
            vertices.append([edge.to_vertex for edge in plan])

        # [['b', 'c', <reisbrein.planner.Point object at 0x7f8eee966630>],
        #  [<reisbrein.planner.Point object at 0x7f8eee966630>],
        #  [<reisbrein.planner.Point object at 0x7f8eee966630>]]

        self.assertEqual(len(vertices), 3)
        self.assertEqual(len(vertices[0]), 3)
        self.assertEqual(len(vertices[1]), 1)
        self.assertEqual(len(vertices[2]), 1)
        self.assertEqual(vertices[0][0], 'b')
        self.assertEqual(vertices[0][1], 'c')
        self.assertEqual(vertices[0][2].location.loc_str, 'e')
        self.assertEqual(vertices[1][0].location.loc_str, 'e')
        self.assertEqual(vertices[2][0].location.loc_str, 'e')

    def test_planner(self):
        p = Planner(Generator())
        vertices = []
        noon = datetime(year=2017, month=11, day=17, hour=12)
        for plan in p.solve('Madurodam', 'Martinitoren', noon):
            vertices.append([edge.to_vertex for edge in plan])

        # print(list(recur_map(str, vertices)))
        # [['Station: Den Haag HS @ 2017-11-17 12:10:00', 'Station: Groningen Noord @ 2017-11-17 12:40:00',
        # 'Martinitoren @ 2017-11-17 12:50:00'], ['Station: Den Haag HS @ 2017-11-17 12:10:00',
        # 'Station: Groningen Noord @ 2017-11-17 12:40:00', 'Martinitoren @ 2017-11-17 12:50:00'], []]

        self.assertEqual(len(vertices), 3)
        self.assertEqual(len(vertices[0]), 3)
        self.assertEqual(len(vertices[1]), 3)
        self.assertEqual(len(vertices[2]), 0)

class TestViews(TestCase):

    def test(self):
        p = Planner(Generator())
        noon = datetime(year=2017, month=11, day=17, hour=12)
        options = p.solve('Madurodam', 'Martinitoren', noon)
        self.assertEqual(PlanView.get_results(options)[0]['travel_time_min'], 50)