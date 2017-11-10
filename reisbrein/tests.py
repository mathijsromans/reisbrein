from django.test import TestCase
from .graph import Graph, shortest_path, Edge
from.planner import Planner
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


class TestPlanner(TestCase):

    def test(self):
        p = Planner()

        vertices = []
        for plan in p.solve('a', 'e'):
            vertices.append([edge.to_vertex for edge in plan])
        self.assertEqual(vertices, [['b', 'c', 'e'], ['d', 'e'], []])

class TestViews(TestCase):

    def test(self):
        p = Planner()
        options = p.solve('a', 'e')
        print(PlanView.get_results(options))