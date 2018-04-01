from . import planner
from django.test import TestCase
from reisbrein.primitives import noon_today, Location

class TestViews(TestCase):

    def setUp(self):
        self.planner = planner.WandelbreinPlanner()
        t = planner.get_default_trail()
        t.save()

    def test(self):
        noon = noon_today()
        self.planner.solve('Utrecht', noon)


class TestTrailPicker(TestCase):

    def setUp(self):
        self.planner = planner.WandelbreinPlanner()
        t1 = planner.get_default_trail()
        t2 = planner.get_default_trail()
        t1.title = 'close trail'
        t2.title = 'far trail'
        t1.begin_lat, t1.begin_lon = 0.5, 0.5
        t2.begin_lat, t2.begin_lon = 1.0, 1.0
        t1.end_lat, t1.end_lon = 0.5, 0.5
        t2.end_lat, t2.end_lon = 1.0, 1.0
        t2.wandelpagina_id = t1.wandelpagina_id + 1
        t1.save()
        t2.save()

    def test_random(self):
        for i in range(0, 50):
            t = planner.get_trail(Location('home', (0, 0)))
            # print(t.title)
