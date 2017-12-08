import requests
import datetime
from website.local_settings import *
from reisbrein.api import cache


class TomTomApi:

    BASE_URL = 'https://api.tomtom.com/'
    ROUTING_URL = 'routing/1/calculateRoute/'
    SEARCHING_URL = 'search/2/geocode/'
    MAP_URL_START = 'https://mydrive.tomtom.com/nl_nl/#mode=routes+routes={"departure":true,"traffic":true,"routeType":"FASTEST","travelMode":"CAR","points":["hw~'
    MAP_URL_END = '"],"avoidCriteria":[]}+ver=3'

    # https://api.tomtom.com/search/2/geocode/madurodam.json?&lat=52.8085&lon=4.4239&idxSet=POI,PAD,Str,Xstr,Geo,Addr
    # https://api.tomtom.com/routing/1/calculateRoute/52.09126,5.12275:52.37317,4.89066/json?key=xxx
    # https://mydrive.tomtom.com/nl_nl/#mode=routes+routes={"departure":true,"traffic":true,"routeType":"FASTEST","travelMode":"CAR","points":["hw~52.09126,5.12275","hw~52.37317,4.89066"],"avoidCriteria":[]}+ver=3


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
        json = cache.query(url, arguments, headers='', expiry=datetime.timedelta(days=1))
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

    def travel_time(self, start, end):
        start_gps = start.gps()
        end_gps = end.gps()
        arguments = { 'key': TOMTOM_APIKEY }
        # headers = {'contentType': 'jsonp'}
        url = TomTomApi.BASE_URL + TomTomApi.ROUTING_URL + \
                str(start_gps[0]) + ',' + \
                str(start_gps[1]) + ':' + \
                str(end_gps[0]) + ',' + \
                str(end_gps[1]) + '/json'
        result = cache.query(url, arguments, headers='', expiry=datetime.timedelta(minutes=5))
        # print(result['routes'][0]['summary'])
        summary = result['routes'][0]['summary']
        time = summary['travelTimeInSeconds']
        delay = summary['trafficDelayInSeconds']
        return time, delay

    @staticmethod
    def map_url(start, end):
        start_gps = start.gps()
        end_gps = end.gps()
        return TomTomApi.MAP_URL_START + str(start_gps[0]) + ',' + str(start_gps[1]) + '","hw~' +\
                                         str(end_gps[0]) + ',' + str(end_gps[1]) + TomTomApi.MAP_URL_END