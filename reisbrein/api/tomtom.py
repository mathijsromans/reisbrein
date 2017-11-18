import requests
import json
from website.local_settings import *

class TomTomApi:

    BASE_URL = 'https://api.tomtom.com/'
    ROUTING_URL = 'routing/1/calculateRoute/'
    SEARCHING_URL = 'search/2/geocode/'

    # https://api.tomtom.com/search/2/geocode/madurodam.json?&lat=52.8085&lon=4.4239&idxSet=POI,PAD,Str,Xstr,Geo,Addr
    def search(self, loc_str):
        arguments = {
            'key': TOMTOM_APIKEY,
            'lat': '52.8085',
            'lon': '4.4239',
            'idxSet': 'POI,PAD,Str,Xstr,Geo,Addr',
            'limit': '1'
        }
        url = TomTomApi.BASE_URL + TomTomApi.SEARCHING_URL + loc_str + '.json'
        # url = TomTomApi.BASE_URL + TomTomApi.SEARCHING_URL + 'madurodam' + '.json?key=' + TOMTOM_APIKEY + '&lat=' \
        #        '52.8085' + '&lon=' + '4.4239' + '&idxSet=POI,PAD,Str,Xstr,Geo,Addr'
        response = requests.get(url, arguments)
        # print(response.url)
        # print(response.content)
        # print(response.json())
        json = response.json()
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

        # LIMIT REACHED...


        start_gps = start.gps()
        end_gps = end.gps()
        arguments = { 'key': TOMTOM_APIKEY }
        # headers = {'contentType': 'jsonp'}
        url = TomTomApi.BASE_URL + TomTomApi.ROUTING_URL + \
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
