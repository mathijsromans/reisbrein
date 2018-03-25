from .planner import WandelbreinPlanner
from django.test import TestCase
from reisbrein.primitives import Location, Point, TransportType, Segment, noon_today
from reisbrein.generator.gen_common import FixTime


class TestViews(TestCase):

    def setUp(self):
        self.planner = WandelbreinPlanner()

    def test(self):
        noon = noon_today()
        plans = self.planner.solve('Utrecht', noon)
