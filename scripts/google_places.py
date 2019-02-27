import requests
import os
import time

URL = 'https://maps.googleapis.com/maps/api/place/'
OUTPUT = 'json'
KEY = 'AIzaSyAZOtnRbMiYCyHWzI7EPhJylNYs-G573Uw'
INPUTTYPE = 'textquery'
PUBLIC_ART_FILE = '../public_art.json'

search_query = 'sculpture'
fields = { 'geometry/location', 'name', 'types', 'place_id'}
queens_bias = 'rectangle:40.7092498169891,-73.85618650635172|40.73060467030399,-73.81966769364828'
mnh_bias = 'rectangle:40.72986238308025,-74.02576541648762|40.72986238308025,-74.02576541648762'

fh_origin = '40.719712,-73.838606'
mnh_origin = '40.727551,-73.998561'
buff_origin = '42.912674,-78.881672'

# Fields to use in the future.
desired_fields = { 'price_level', 'photos'}

def search_one():
    target = 'findplacefromtext'
    url = os.path.join(URL, target, OUTPUT)
    payload = {
                'locationbias': mnh_bias,
                'input': search_query,
                'inputtype': INPUTTYPE,
                'fields': ','.join(fields),
                'key': KEY
            }
    r = requests.get(url, params=payload)
    return r

def has_next(json):
    return 'next_page_token' in json

def search_nearby(origin_location=fh_origin, radius=5000):
    target = 'nearbysearch'
    url = os.path.join(URL, target, OUTPUT)
    payload = {
            'key': KEY,
            'location': origin_location,
            'rankby': 'distance',
            #'radius': radius,
            'keyword': search_query
    }
    r = requests.get(url, params=payload)
    j = r.json()
    results = j['results']
    while has_next(j):
        time.sleep(3)
        print('Querying next page..')
        payload = {
            'key': KEY,
            'pagetoken': j['next_page_token']
        }
        r = requests.get(url, params=payload)
        j = r.json()
        results = results + j['results']

    return results

'''
Convert from the existing google schema to our simpler schema
We want:
    location { lat, lon }
    name
    description
    date_added

Eventually:
    photo
'''
def convert_from_places_to_freedom(place_dict):
    pass
