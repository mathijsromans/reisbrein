import requests
import datetime
from reisbrein.primitives import TransportType
from reisbrein.api import cache
from website.local_settings import OPENROUTESERVICE_APIKEY

# Note that adding 'format=geojson' gives a different result
# https://api.openrouteservice.org/directions?api_key=your-api-key&coordinates=8.34234%2C48.23424%7C8.34423%2C48.26424&profile=driving-car
# https://maps.openrouteservice.org/directions?n1=52.645894&n2=5.431427&n3=9&a=52.099476,4.297198,53.219382,6.568204&b=1a&c=0&g1=-1&g2=0&h2=3&k1=en-US&k2=km

BASE_API_URL = 'https://api.openrouteservice.org/directions'
BASE_MAP_URL = 'https://maps.openrouteservice.org/directions'

translate_mode = {
    # TransportType.WAIT: '',
    TransportType.WALK: 'foot-walking',
    # TransportType.TRAIN: '',
    TransportType.BIKE: 'cycling-road',
    TransportType.CAR: 'driving-car',
    # TransportType.BUS: '',
    # TransportType.TRAM: '',
    TransportType.OVFIETS: 'cycling-road',
}

def travel_time(start, end, mode):
    try:
        arguments = [
            ('api_key', OPENROUTESERVICE_APIKEY),
            ('coordinates', str(start.gps[1]) + ',' + str(start.gps[0]) + '|' +
                            str(end.gps[1])   + ',' + str(end.gps[0])),
            ('profile', translate_mode[mode]),
            # ('preference', 'fastest'),
            # ('format', 'geojson'),
            # ('units', 'm'),
            # ('language', 'en'),
            ('geometry', 'false'),
            # ('geometry_format', 'encodedpolyline'),
            # ('geometry_simplify', ''),
            ('instructions', 'false'),
            # ('instructions_format', 'text'),
            # ('roundabout_exits', ''),
            # ('attributes', ''),
            # ('maneuvers', ''),
            ('radiuses', '-1|-1'),  # seems to have no effect
            # ('bearings', ''),
            # ('continue_straight', ''),
            # ('elevation', ''),
            # ('extra_info', 'steepness'),
            # ('optimized', 'true'),
            # ('options', '{}'),
            # ('id', '')
        ]

        headers = {}

        result = cache.query(BASE_API_URL, arguments, headers, expiry=datetime.timedelta(days=7))
        response = requests.Request('GET', BASE_API_URL, params=arguments).prepare()
        # print(response.url)
        # print(response.json())
        # print(result['routes'][0]['summary']['duration'])
        time_sec = int(result['routes'][0]['summary']['duration'])
        # print('openrouteserviceapi.travel_time ' + str(start_gps) + ' -> ' + str(end_gps) + ': ' + str(datetime.timedelta(seconds=time_sec)))
    except (KeyError, IndexError) as error:
        print('Failed with start=' + str(start) + ', end=' + str(end) + ', profile=' + str(translate_mode[mode]))
        print('Failed with route ' + map_url(start, end, mode))
        # check for "Connection between locations not found"
        if 'error' in result and 'code' in result['error'] and result['error']['code'] == 2099:
            time_sec = 99999
        else:
            raise ValueError
    return time_sec


def map_url(start, end, mode):
    arguments = [
        # ('n1', '52.645894'),
        # ('n2', '5.431427'),
        ('n3', '9'),
        # note that lat/lon are reversed here...
        ('a', str(start.gps[0]) + ',' +
              str(start.gps[1]) + ',' +
              str(end.gps[0])   + ',' +
              str(end.gps[1])),
        ('b', '1a'),
        ('c', '0'),
        ('g1', '-1'),
        ('g2', '0'),
        ('h2', '3'),
        ('k1', 'en-US'),
        ('k2', 'km')
    ]
    p = requests.Request('GET', BASE_MAP_URL, params=arguments).prepare()
    return p.url