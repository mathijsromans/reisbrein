from django.test import TestCase
from website.local_settings import *
from ns_api import *


class TestNSAPI(TestCase):

    def setUp(self):
        self.nsapi = NSAPI(NSAPI_USERNAME, NSAPI_KEY)

    def testStations(self):
        # commented-out because NSAPI_USERNAME, NSAPI_KEY need to be set
        # stations = self.nsapi.get_stations()
        # self.assertGreater(len(stations), 10)



