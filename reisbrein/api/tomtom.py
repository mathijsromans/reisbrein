import datetime
from website.local_settings import *
from reisbrein.api import cache

class TomTomApi:

    BASE_URL = 'https://api.tomtom.com/'
    ROUTING_URL = 'routing/1/calculateRoute/'
    SEARCHING_URL = 'search/2/geocode/'
    MAP_URL_START = 'https://mydrive.tomtom.com/nl_nl/#mode=routes+routes={"departure":true,"traffic":true,"routeType":"FASTEST","travelMode":"CAR","points":["hw~'
    MAP_URL_END = '"],"avoidCriteria":[]}+ver=3'

    # Routing API documentation: https://developer.tomtom.com/online-routing/online-routing-documentation-routing/calculate-route
    # Examples:
    # https://api.tomtom.com/search/2/geocode/madurodam.json?&lat=52.8085&lon=4.4239&idxSet=POI,PAD,Str,Xstr,Geo,Addr
    # https://api.tomtom.com/routing/1/calculateRoute/52.09126,5.12275:52.37317,4.89066/json?key=xxx
    # https://mydrive.tomtom.com/nl_nl/#mode=routes+routes={"departure":true,"traffic":true,"routeType":"FASTEST","travelMode":"CAR","points":["hw~52.09126,5.12275","hw~52.37317,4.89066"],"avoidCriteria":[]}+ver=3

    class RouteParams:

        def __init__(self, start, end, avoid_highways=False):
            self.start = start
            self.end = end
            self.avoid_highways = avoid_highways

    def search(self, loc_str):
        arguments = {
            'key': TOMTOM_APIKEY,
            'countrySet': 'NL',
            'lat': '52.8085',
            'lon': '4.4239',
            'idxSet': 'POI,PAD,Str,Xstr,Geo,Addr',
            'limit': '1'
        }
        url = TomTomApi.BASE_URL + TomTomApi.SEARCHING_URL + loc_str + '.json'
        # url = TomTomApi.BASE_URL + TomTomApi.SEARCHING_URL + 'madurodam' + '.json?key=' + TOMTOM_APIKEY + '&lat=' \
        #        '52.8085' + '&lon=' + '4.4239' + '&idxSet=POI,PAD,Str,Xstr,Geo,Addr'
        json = cache.query_from(url, arguments, headers=dict(), expiry=datetime.timedelta(days=1))
        try:
            loc = json['results'][0]['position']
            result = (float(loc['lat']), float(loc['lon']))
            # print(result)
            return result
        except KeyError:
            pass
        except IndexError:
            pass
        return None

    def travel_time(self, route_params):
        start_gps = route_params.start.gps
        end_gps = route_params.end.gps
        arguments = {'key': TOMTOM_APIKEY}
        if route_params.avoid_highways:
            arguments['avoid'] = 'motorways'
        # headers = {'contentType': 'jsonp'}
        url = TomTomApi.BASE_URL + TomTomApi.ROUTING_URL + \
                str(start_gps[0]) + ',' + \
                str(start_gps[1]) + ':' + \
                str(end_gps[0]) + ',' + \
                str(end_gps[1]) + '/json'
        result = cache.query_from(url, arguments, headers=dict(), expiry=datetime.timedelta(minutes=5))
        # print(result['routes'][0]['summary'])
        summary = result['routes'][0]['summary']
        time = summary['travelTimeInSeconds']
        delay = summary['trafficDelayInSeconds']
        return time, delay

    @staticmethod
    def map_url(route_params):
        start_gps = route_params.start.gps
        end_gps = route_params.end.gps
        return TomTomApi.MAP_URL_START + str(start_gps[0]) + ',' + str(start_gps[1]) + '","hw~' +\
                                         str(end_gps[0]) + ',' + str(end_gps[1]) + TomTomApi.MAP_URL_END