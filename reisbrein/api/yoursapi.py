import requests
import datetime
from reisbrein.primitives import TransportType
from reisbrein.api import cache

# see: http://wiki.openstreetmap.org/wiki/YOURS
# http://yournavigation.org/api/1.0/gosmore.php?format=geojson&flat=52.215676&flon=5.963946&tlat=52.2573&tlon=6.1799&v=motorcar&fast=1&layer=mapnik
# http://yournavigation.org/?flat=52.215676&flon=5.963946&tlat=52.2573&tlon=6.1799&v=bicycle&fast=1&layer=mapnik
BASE_URL = 'http://yournavigation.org/'
API_PATH = 'api/1.0/gosmore.php'

travel_time_cache = {}  # global variable is it ok?

translate_mode = {
    # TransportType.WAIT: '',
    TransportType.WALK: 'foot',
    # TransportType.TRAIN: '',
    TransportType.BIKE: 'bicycle',
    TransportType.CAR: 'motorcar',
    # TransportType.BUS: '',
    # TransportType.TRAM: '',
    TransportType.OVFIETS: 'bicycle',
}


def get_common_args(start_gps, end_gps, mode):
    # note that yournavigation.org DOES care about order: lat must come before lon, therefore use a list, not dict
    return [
        ('flat', start_gps[0]),
        ('flon', start_gps[1]),
        ('tlat', end_gps[0]),
        ('tlon', end_gps[1]),
        ('v', translate_mode[mode]),
        ('fast', 1),
        ('layer', 'mapnik'),  # Provide 'cn' for using bicycle routing using cycle route networks only.
    ]

def do_travel_time_sec(start_gps, end_gps, mode):
    try:
        arguments = get_common_args(start_gps, end_gps, mode)
        arguments.append(('format', 'geojson'))


        # as requested by http://wiki.openstreetmap.org/wiki/YOURS#Version_1.0
        headers = {'X-Yours-client': 'www.reisbrein.nl'}

        result = cache.query(BASE_URL + API_PATH, arguments, headers, expiry=datetime.timedelta(days=7))
        # response = requests.get(BASE_URL + API_PATH, arguments, headers=headers)
        # print(response.url)
        # print(response.json())
        # print(result['routes'][0]['summary'])
        time_sec = int(result['properties']['traveltime'])
        # print('yoursapi.travel_time ' + str(start) + ' -> ' + str(end) + ': ' + str(datetime.timedelta(seconds=time_sec)))
        return time_sec
    except (KeyError, IndexError) as error:
        raise ValueError


def travel_time(start_gps, end_gps, mode):
    try:
        return travel_time_cache[(start_gps, end_gps, mode)]
    except KeyError:
        time_sec = do_travel_time_sec(start_gps, end_gps, mode)
        travel_time_cache[(start_gps, end_gps, mode)] = time_sec
        return time_sec


def map_url(start, end, mode):
    arguments = get_common_args( start.gps(), end.gps(), mode)
    p = requests.Request('GET', BASE_URL, params=arguments).prepare()
    return p.url