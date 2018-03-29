import logging
import requests
import datetime
from reisbrein.primitives import TransportType, Location
from reisbrein.api import cache
from website.local_settings import OPENROUTESERVICE_APIKEY
from geopy.distance import vincenty
from copy import deepcopy


logger = logging.getLogger(__name__)

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


class ConnectionNotFoundError(Exception):
    pass


def try_travel_time(start, end, mode):
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

        q = cache.Query(None, BASE_API_URL, arguments, headers, datetime.timedelta(days=7))
        result = cache.query(q)
        # print(response.url)
        # print(response.json())
        # print(result['routes'][0]['summary']['duration'])
        time_sec = int(result['routes'][0]['summary']['duration'])
        # print('openrouteserviceapi.travel_time ' + str(start_gps) + ' -> ' + str(end_gps) + ': ' + str(datetime.timedelta(seconds=time_sec)))
    except (KeyError, IndexError) as error:
        response = requests.Request('GET', BASE_API_URL, params=arguments).prepare()
        logger.error('Failed with start=' + str(start) + ', end=' + str(end) + ', profile=' + str(translate_mode[mode]))
        logger.error('Failed URL = ' + str(response.url))
        logger.error('Failed with route ' + map_url(start, end, mode))
        if 'error' in result:
            if result['error'] == 'Rate limit exceeded':
                logger.error('Rate limit exceeded')
                cache.remove_cache(q)
            if 'message' in result['error']:
                logger.error('Error message: ' + result['error']['message'])
            if 'code' in result['error']:
                logger.error('Error code: ' + str(result['error']['code']))
                if result['error']['code'] == 2009 or result['error']['code'] == 2099:
                    raise ConnectionNotFoundError()
        raise ValueError
    return time_sec


def travel_time_and_map_url(start, end, mode):
    # because openrouteservice has trouble finding bike-routes, e.g. from Utrecht Centraal, we try to find other locations
    # where we can bike from
    jump_closer_distance = 100
    bicycle_speed = 18/3.6
    local_start = deepcopy(start)
    local_end = deepcopy(end)
    for i in range(0, 3):
        try:
            # print('Trying with locations ' + local_start.full_str() + ', ' + local_end.full_str())
            extra_time = i * jump_closer_distance / bicycle_speed
            time_sec = try_travel_time(local_start, local_end, mode) + extra_time
            return time_sec, map_url(local_start, local_end, mode)
        except ConnectionNotFoundError as error:
            distance = vincenty(local_start.gps, local_end.gps).meters
            new_start = Location.midpoint(local_start, local_end, jump_closer_distance/distance)
            new_end = Location.midpoint(local_start, local_end, (distance-jump_closer_distance)/distance)
            local_start = new_start
            local_end = new_end
    return 99999, map_url(local_start, local_end, mode)  # no bike route found, please ignore


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