from .planner import WandelbreinPlanner
from django.test import TestCase
from reisbrein.primitives import noon_today
from wandelbrein.models import Trail


class TestViews(TestCase):

    def setUp(self):
        self.planner = WandelbreinPlanner()
        t = Trail(
            title = 'GW660 / Bemmel: Bemmelse Waard',
            wandelpagina_id = 17454,
            wandelpagina_url = 'http://www.wandelzoekpagina.nl/dagwandelingen/wandeling.php?wnummer=17454',
            nswandel_url = 'http://nswandel.nl/Album/GW-Bemmel-660/index.html',
            begin_lon = 5.895478,
            begin_lat = 51.8929925,
            end_lon = 5.8954863,
            end_lat = 51.8929898,
            distance = 14158.4412752064,
        )
        t.save()

    def test(self):
        noon = noon_today()
        plans = self.planner.solve('Utrecht', noon)
