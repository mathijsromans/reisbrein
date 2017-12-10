import requests
import json
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
    PLANNERSTACK_BASE_URL = 'http://demo.planner.plannerstack.com/otp/routers/default/plan'

    @staticmethod
    def search(start, end, start_time):
        # logger.info('BEGIN')
        log_start = time.time()
        start_gps = start.gps()
        end_gps = end.gps()
        arguments = {
            'fromPlace' : str(start_gps[0]) + ',' + str(start_gps[1]),
            'toPlace' : str(end_gps[0]) + ',' + str(end_gps[1]),
            'arriveBy' : 'false',
            'maxWalkDistance' : '3000',
            'mode' : 'TRANSIT,WALK',
            'date' : str(start_time.month) + '-' + str(start_time.day) + '-' + str(start_time.year),
            'time' : str(start_time.hour) + ':' + str(start_time.minute),
            # 'api_key' : MONOTCH_APIKEY,
        }
        headers = {'Content-Type': 'application/json'}
        result = cache.query(MonotchApi.PLANNERSTACK_BASE_URL, arguments, headers, expiry=datetime.timedelta(minutes=15))
        log_end = time.time()
        # logger.info('END - time: ' + str(log_end - log_start))
        return result['plan']

