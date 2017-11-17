import requests
import json

BASE_URL = 'https://api-c.thequestionmark.org/api/v1.2/'

def search_by_string(params):
    params_as_string = json.dumps(params)
    response = requests.get(BASE_URL + 'products/', params)
    foo = json.dumps(response.json())
    # with open('query', 'w') as f:
    #     f.write(foo)
    result= json.loads(foo)
    return result
