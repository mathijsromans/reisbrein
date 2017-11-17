import requests
import json
from website.local_settings import *


class TomTomApi:

    BASE_URL = 'https://api.tomtom.com/routing/1/calculateRoute/'

    def travel_time(self, start, end):
        start_gps = start.gps()
        end_gps = end.gps()
        arguments = { 'key': TOMTOM_APIKEY }
        # headers = {'contentType': 'jsonp'}
        url = TomTomApi.BASE_URL + \
                str(start_gps[0]) + ',' + \
                str(start_gps[1]) + ':' + \
                str(end_gps[0]) + ',' + \
                str(end_gps[1]) + '/json'
        response = requests.get(url, arguments)
        # print(response.url)
        # print(response.json())
        result = response.json()
        # print(result['routes'][0]['summary'])
        time = result['routes'][0]['summary']['travelTimeInSeconds']
        return time
