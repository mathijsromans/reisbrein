import requests
import json
from website.local_settings import *

#http://api.openweathermap.org/data/2.5/weather?q=Den%20Haag,nl&APPID=xxx

class WeatherApi:

    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

    def search(self, city):
        arguments = {
            'q': city,
            'APPID': OPENWEATHERMAP_APIKEY
        }
        url = WeatherApi.BASE_URL
        response = requests.get(url, arguments)
        # print(response.url)
        # print(response.content)
        # print(response.json())
        json = response.json()
        # print(json)
        weather = json['weather'][0]['main']
        icon = 'http://openweathermap.org/img/w/' + json['weather'][0]['icon'] + '.png'
        return weather, icon
