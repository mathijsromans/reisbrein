import requests
import json
from website.local_settings import *

# BASE_URL + ?fromPlace=51.923943445544715%2C4.4659423828125&toPlace=52.38901106223458%2C4.9658203125&arriveBy=false&
# maxWalkDistance=3000&mode=TRANSIT%2CWALK&api_key=dnjttz9xhbdsm89ba6wpymwu


class MonotchApi:

    BASE_URL = 'https://api.monotch.com/plannerstack/v1/routers/default/plan/'

    def search(self, start, end, start_time):
        start_gps = start.gps()
        end_gps = end.gps()
        arguments = {
            'fromPlace' : str(start_gps[0]) + ',' + str(start_gps[1]),
            'toPlace' : str(end_gps[0]) + ',' + str(end_gps[1]),
            'arriveBy' : 'false',
            'maxWalkDistance' : '3000',
            'mode' : 'TRANSIT,WALK',
            'date' : '11-17-2017',
            'time' : str(start_time.hour) + ':' + str(start_time.minute),
            'api_key' : MONOTCH_APIKEY
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.get(MonotchApi.BASE_URL, arguments, headers=headers)
        # print(response.text)
        # print(response.url)
        # print(response.json())
        foo = json.dumps(response.json())
        result = json.loads(foo)
        return result['plan']

