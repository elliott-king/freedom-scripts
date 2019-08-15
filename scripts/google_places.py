import requests
import os
import time

import es_upload 
import dyn_upload
import convert_places_for_dynamo

URL = 'https://maps.googleapis.com/maps/api/place/'
OUTPUT = 'json'
# DO NOT SUBMIT: cannot make git repo public now.
# Maybe store elsewhere on disk
KEY = 'AIzaSyCZ21RlCa8IVwxR-58b8fTgUXn_a4UYhbc'
INPUTTYPE = 'textquery'
PUBLIC_ART_FILE = '../public_art.json'

search_query = 'sculpture'
fields = { 'geometry/location', 'name', 'types', 'place_id'}
queens_bias = 'rectangle:40.7092498169891,-73.85618650635172|40.73060467030399,-73.81966769364828'
mnh_bias = 'rectangle:40.72986238308025,-74.02576541648762|40.72986238308025,-74.02576541648762'

fh_origin = '40.719712,-73.838606'
jh_origin = '40.750613,-73.878024'
mnh_origin = '40.727551,-73.998561'
buff_origin = '42.912674,-78.881672'
jersey_city_origin = '40.720474,-74.043823'

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

# Place api allows for up to three pages of results.
def has_next(json):
    return 'next_page_token' in json

def search_nearby(origin_location=fh_origin):
    target = 'nearbysearch'
    url = os.path.join(URL, target, OUTPUT)
    payload = {
            'key': KEY,
            'location': origin_location,
            'rankby': 'distance',
            # No need for radius when we rank by distance.
            # Returned objects will still be within some max radius
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

def search_and_upload(origin_location):
    client = es_upload.client()
    items_from_google = search_nearby(origin_location)
    print(f"Pulled {len(items_from_google)} items from google places api.")

    from_dynamo = dyn_upload.get_all_items_from_table(dyn_upload.BETA_TABLE)
    names = set()
    for item in from_dynamo:
        names.add(item['name'])

    for item in items_from_google:
        if item['name'] not in names:
            item = convert_places_for_dynamo.convert_place_object(item)
            dyn_upload.add_items_to_table(
                    dyn_upload.BETA_TABLE, [item])
            item = es_upload.dyn_document_to_es_document(item)
            es_upload.index(client, item)
