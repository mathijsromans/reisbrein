import requests
import enum
import datetime

# see: http://wiki.openstreetmap.org/wiki/YOURS
# http://yournavigation.org/api/1.0/gosmore.php?format=geojson&flat=52.215676&flon=5.963946&tlat=52.2573&tlon=6.1799&v=motorcar&fast=1&layer=mapnik
# http://yournavigation.org/?flat=52.215676&flon=5.963946&tlat=52.2573&tlon=6.1799&v=bicycle&fast=1&layer=mapnik
BASE_URL = 'http://yournavigation.org/'
API_PATH = 'api/1.0/gosmore.php'

cache = {}  # global variable is it ok?

class Mode(enum.Enum):
    CAR = 'motorcar'
    BIKE = 'bicycle'
    WALK = 'foot'  # currently not working?

def get_common_args(start_gps, end_gps, mode):
    # note that yournavigation.org DOES care about order: lat must come before lon, therefore use a list, not dict
    return [
        ('flat', start_gps[0]),
        ('flon', start_gps[1]),
        ('tlat', end_gps[0]),
        ('tlon', end_gps[1]),
        ('v', mode.value),
        ('fast', 1),
        ('layer', 'mapnik'),  # Provide 'cn' for using bicycle routing using cycle route networks only.
    ]

def do_travel_time(start_gps, end_gps, mode):
    try:
        arguments = get_common_args(start_gps, end_gps, mode)
        arguments.append(('format', 'geojson'))

        # as requested by http://wiki.openstreetmap.org/wiki/YOURS#Version_1.0
        headers = {'X-Yours-client': 'www.reisbrein.nl'}

        response = requests.get(BASE_URL + API_PATH, arguments, headers=headers)
        # print(response.url)
        # print(response.json())
        result = response.json()
        # print(result['routes'][0]['summary'])
        time = int(result['properties']['traveltime'])
        # print('yoursapi.travel_time ' + str(start) + ' -> ' + str(end) + ': ' + str(datetime.timedelta(seconds=time)))
        return time
    except (KeyError, IndexError) as error:
        raise ValueError


def travel_time(start, end, mode):
    start_gps = start.gps()
    end_gps = end.gps()
    try:
        return cache[(start_gps, end_gps, mode)]
    except KeyError:
        result = do_travel_time(start_gps, end_gps, mode)
        cache[(start_gps, end_gps, mode)] = result
        return result


def map_url(start, end, mode):
    arguments = get_common_args( start.gps(), end.gps(), mode)
    p = requests.Request('GET', BASE_URL, params=arguments).prepare()
    return p.url