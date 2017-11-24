import requests
import datetime
from reisbrein.primitives import Location

class RdwApi:

# https://opendata.rdw.nl/resource/8u4d-s4q7.json?usageid=PARKRIDE
# https://opendata.rdw.nl/resource/nsk3-v9n7.json?areaid=%22599_PERNIS%22

    BASE_URL = 'https://opendata.rdw.nl/resource/'
    PARK_URL = '8u4d-s4q7.json'
    AREA_URL = 'nsk3-v9n7.json'
    AREA_LIMIT = 10000
    parkings = []
    last_update = datetime.datetime(year=1970, month=1, day=1)

    @staticmethod
    def get_json(suburl, arguments = {}):
        url = RdwApi.BASE_URL + suburl
        response = requests.get(url, arguments)
        return response.json()

    @staticmethod
    def get_park_and_ride_json():
        arguments = {
            'usageid': 'PARKRIDE',
        }
        return RdwApi.get_json(RdwApi.PARK_URL, arguments)

    @staticmethod
    def get_area_json():
        arguments = {
            '$limit': RdwApi.AREA_LIMIT,
        }
        json = RdwApi.get_json(RdwApi.AREA_URL, arguments)
        if len(json) == RdwApi.AREA_LIMIT:
            print('WARNING: More results from RDW may be available')
        return json

    @staticmethod
    def do_get_park_and_rides():
        pr_json = RdwApi.get_park_and_ride_json()
        area_json = RdwApi.get_area_json()
        RdwApi.parkings = []
        # print('found ' + str(len(pr_json)) + ' parkings')
        # print('found ' + str(len(area_json)) + ' areas')
        for item in pr_json:
            try:
                areaid = item['areaid']
                area = next(a for a in area_json if a['areaid']==areaid)
                # area['areageometryastext'] = 'POINT (4.382199252 51.884720263)'
                geo_text = area['areageometryastext'].translate(str.maketrans('','','()')).split()
                if geo_text[0] == 'POINT':
                    loc_name = item['areadesc'].replace('&amp;', '&')  # unfortunately there are xml-escapes in the json...
                    parking = Location(loc_name, (float(geo_text[2]), float(geo_text[1])))  # reversed!
                    parking.has_parking = True
                    RdwApi.parkings.append(parking)
                else:
                    print ('no point in ' < str(geo_text[0]))
            except (StopIteration, KeyError, IndexError):
                pass
        # for p in parkings:
        #     print(str(p) + ' at ' + str(p.gps()))
        # print(str(len(parkings)) + ' parkings have a location')
        RdwApi.last_update = datetime.datetime.now()

    @staticmethod
    def get_park_and_rides():
        if datetime.datetime.now() - RdwApi.last_update > datetime.timedelta(hours=24):
            # print('creating new parkings')
            RdwApi.do_get_park_and_rides()
        return RdwApi.parkings
