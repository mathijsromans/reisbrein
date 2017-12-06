import requests
import datetime
import json
from website.local_settings import *
from reisbrein.api import cache

#http://api.openweathermap.org/data/2.5/weather?q=Den%20Haag,nl&APPID=xxx

class WeatherApi:

    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

    def search(self, city):
        arguments = {
            'q': city,
            'APPID': OPENWEATHERMAP_APIKEY
        }
        url = WeatherApi.BASE_URL
        result = cache.query(url, arguments, headers='', expiry=datetime.timedelta(minutes=15))
        weather = ''
        icon = ''
        try:
            weather = result['weather'][0]['main']
            icon = 'http://openweathermap.org/img/w/' + result['weather'][0]['icon'] + '.png'
        except KeyError:
            pass
        except IndexError:
            pass
        return weather, icon
