from .planner import WandelbreinPlanner, get_default_trail
from django.test import TestCase
from reisbrein.primitives import noon_today
from wandelbrein.models import Trail


class TestViews(TestCase):

    def setUp(self):
        self.planner = WandelbreinPlanner()
        t = get_default_trail()
        t.save()

    def test(self):
        noon = noon_today()
        plans, trail = self.planner.solve('Utrecht', noon)
