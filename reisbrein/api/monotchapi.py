from recordclass import recordclass
import datetime
import logging
import time
from website.local_settings import *
from reisbrein.api import cache

# MONOTCH_BASE_URL      + ?fromPlace=51.923943445544715%2C4.4659423828125&toPlace=52.38901106223458%2C4.9658203125&arriveBy=false&maxWalkDistance=3000&mode=TRANSIT%2CWALK&api_key=dnjttz9xhbdsm89ba6wpymwu
# PLANNERSTACK_BASE_URL + ?fromPlace=51.923943445544715%2C4.4659423828125&toPlace=52.38901106223458%2C4.9658203125&mode=TRANSIT%2CWALK&maxWalkDistance=3000&arriveBy=false&wheelchair=false

logger = logging.getLogger(__name__)


class MonotchApi:

    MONOTCH_BASE_URL = 'https://api.monotch.com/plannerstack/v1/routers/default/plan/'
    PLANNERSTACK_DEMO_URL = 'http://demo.planner.plannerstack.com/otp/routers/default/plan'
    PLANNERSTACK_PRODUCTION_URL = 'http://planner.plannerstack.com/otp/routers/default/plan'

    Request = recordclass('Request', ['start', 'end', 'start_time', 'result'])

    def __init__(self):
        self.requests = []

    def add_search_request(self, start, end, start_time):
        request = self.Request(start, end, start_time, None)
        self.requests.append(request)
        return request

    def do_requests(self):
        for r in self.requests:
            # logger.info('BEGIN')
            log_start = time.time()
            start_gps = r.start.gps()
            end_gps = r.end.gps()
            arguments = {
                'fromPlace' : str(start_gps[0]) + ',' + str(start_gps[1]),
                'toPlace' : str(end_gps[0]) + ',' + str(end_gps[1]),
                'arriveBy' : 'false',
                'maxWalkDistance' : '3000',
                'mode' : 'TRANSIT,WALK',
                'date' : str(r.start_time.month) + '-' + str(r.start_time.day) + '-' + str(r.start_time.year),
                'time' : str(r.start_time.hour) + ':' + str(r.start_time.minute),
                # 'api_key' : MONOTCH_APIKEY,
            }
            headers = {'Content-Type': 'application/json'}
            url = MonotchApi.PLANNERSTACK_PRODUCTION_URL if PRODUCTION_SERVER else MonotchApi.PLANNERSTACK_DEMO_URL
            query_out = cache.query(url, arguments, headers, expiry=datetime.timedelta(minutes=15))
            log_end = time.time()
            # logger.info('END - time: ' + str(log_end - log_start))

            r.result = query_out['plan']

