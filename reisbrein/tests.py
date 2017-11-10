from django.test import TestCase
from .graph import Graph, shortest_path, Edge
from.planner import Planner


class TestTest(TestCase):
    """ Example test case. """

    def test_asserts(self):
        """ Example unit test. Tests unittest asserts. """
        self.assertTrue(True)
        self.assertEqual(True, True)
        self.assertNotEqual(True, False)


class TestGraph(TestCase):

    def test_asserts(self):
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

        self.assertEqual(shortest_path(G, 'a', 'e'), ['a', 'b', 'c', 'e'])


class TestPlanner(TestCase):

    def test_asserts(self):
        p = Planner()
        self.assertEqual(p.solve('a', 'e'), ['a', 'b', 'c', 'e'])