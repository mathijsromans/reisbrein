from datetime import datetime
from django.test import TestCase
from .graph import Graph, shortest_path, Edge
from .planner import DijkstraPlanner, RichPlanner, Location, recur_map
from reisbrein.generator.generator import TestGenerator, Generator
from .views import PlanView


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
        self.assertEqual(loc.gps(), (52.09126, 5.12275))
        loc2 = Location('ddd-unknown-location-ddsfaasdfasdf')
        self.assertEqual(loc2.gps(), None)


class TestDijkstraPlanner(TestCase):

    def test_fixed_generator(self):
        p = DijkstraPlanner(TestGenerator())

        vertices = []
        noon = datetime(year=2017, month=11, day=17, hour=12)
        for plan in p.solve('a', 'e', noon):
            vertices.append([edge.to_vertex for edge in plan])

        # [['b', 'c', <reisbrein.planner.Point object at 0x7f8eee966630>],
        #  [<reisbrein.planner.Point object at 0x7f8eee966630>],
        #  [<reisbrein.planner.Point object at 0x7f8eee966630>]]

        # self.assertEqual(len(vertices), 3)
        # self.assertEqual(len(vertices[0]), 3)
        # self.assertEqual(vertices[0][0], 'b')
        # self.assertEqual(vertices[0][1], 'c')
        # self.assertEqual(vertices[0][2].location.loc_str, 'e')

    def test_planner(self):
        p = DijkstraPlanner(Generator())
        vertices = []
        noon = datetime(year=2017, month=11, day=17, hour=12)
        for plan in p.solve('Madurodam', 'Martinitoren', noon):
            vertices.append([edge.to_vertex for edge in plan])

        # print(list(recur_map(str, vertices)))
        # [['Station: Den Haag HS @ 2017-11-17 12:10:00', 'Station: Groningen Noord @ 2017-11-17 12:40:00',
        # 'Martinitoren @ 2017-11-17 12:50:00'], ['Station: Den Haag HS @ 2017-11-17 12:10:00',
        # 'Station: Groningen Noord @ 2017-11-17 12:40:00', 'Martinitoren @ 2017-11-17 12:50:00'], []]

        # self.assertEqual(len(vertices), 2)
        # self.assertEqual(len(vertices[0]), 1)
        # self.assertEqual(len(vertices[1]), 1)
        # self.assertEqual(len(vertices[2]), 1)


class TestRichPlanner(TestCase):

    def test_fixed_generator(self):
        p = RichPlanner(TestGenerator())

        vertices = []
        noon = datetime(year=2017, month=11, day=17, hour=12)
        plans = p.solve('a', 'e', noon)
        for plan in plans:
            vertices.append([edge.to_vertex for edge in plan])
        # print(list(recur_map(str, plans)))

        # self.assertEqual(len(plans), 4)
        # self.assertEqual(len(plans[0]), 3)
        # self.assertEqual(len(plans[1]), 2)

    def test_planner(self):
        p = RichPlanner(Generator())
        vertices = []
        noon = datetime(year=2017, month=11, day=17, hour=12)
        plans = p.solve('Madurodam', 'Martinitoren', noon)
        for plan in plans:
            vertices.append([edge.to_vertex for edge in plan])
        # print(list(recur_map(str, vertices)))

        # self.assertEqual(len(plans), 4)
        # self.assertEqual(len(plans[0]), 4)
        # self.assertEqual(len(plans[1]), 4)


class TestViews(TestCase):

    def test(self):
        p = RichPlanner(Generator())
        time = datetime(year=2017, month=11, day=18, hour=9)
        plans = p.solve('Den Haag', 'Nieuwegein', time)
        results = PlanView.get_results(plans)
        # print(results)
        self.assertEqual(len(plans), 3)
        self.assertEqual(results[0]['travel_time_min'], 43)
