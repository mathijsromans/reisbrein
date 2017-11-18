import requests
import json
from website.local_settings import *
from reisbrein.models import MapQuestCache

class MapQuestApi:

    BASE_URL = 'http://www.mapquestapi.com/geocoding/v1/address'

# http://www.mapquestapi.com/geocoding/v1/address?key=rN3kTTmsHz0aA1Xz1ABvkaaGGcEtXKO6&location=Washington,DC
    def search(self, loc_str):
        query, created = MapQuestCache.objects.get_or_create(search=loc_str)
        if not created:
            # print(query.lat, query.lon)
            return (query.lat, query.lon)
        # else:
        #     print('found!')
        arguments = {
            'key': MAPQUEST_APIKEY,
            'location': loc_str
        }
        url = MapQuestApi.BASE_URL
        response = requests.get(url, arguments)
        # print(response.url)
        # print(response.content)
        # print(response.json())
        json = response.json()
        # print(json)
        try:
            loc = json['results'][0]['locations'][0]['latLng']
            result = (float(loc['lat']), float(loc['lng']))
            query.lat = result[0]
            query.lon = result[1]
            query.save()
            # print(query.lat, query.lon)
            return (query.lat, query.lon)
        except KeyError:
            pass
        except IndexError:
            pass
        return None
