""" Change a Google Place object into the format we prefer.
We will keep track of flagging in a seperate table.

As of 03/21/19, we are storing all objects from the Google Place API first in 
their own db (to retain consistency). Update this when that changes. 

End goal: download from Places, the upload to ES and DynamoDB simultaneously.

Useful objects that ES may or may not need, but our DynamoDB table will:
- photo
  - link
  - reference
- location
- name of location
- hashed id (ours)
- type (public art, sculpture)
- date added (TODO: unify this between es_sculptures and this)

- user who uploaded (TODO)
"""

import time
import requests 
import uuid

# TODO: can't yet handle array of types
# _TYPES = ['sculpture', 'public']
_TYPE = 'sculpture'
_PHOTO_MAXHEIGHT = 400

def get_photo(photo):
    url = 'https://maps.googleapis.com/maps/api/place/photo'
    payload = {
            'key': 'AIzaSyCZ21RlCa8IVwxR-58b8fTgUXn_a4UYhbc',
            'maxheight': _PHOTO_MAXHEIGHT,
            'photoreference': photo['photo_reference']
    }
    r = requests.get(url, params=payload)
    return r


def convert_place_object(place):
    location = {
        'name': place['name'],
#        'location': place['geometry']['location'],
        'location': {
            'lat': place['geometry']['location']['lat'],
            'lon': place['geometry']['location']['lng']
            },
        'date_added': time.time(),
        # TODO: support list of types (see above)
        'type': _TYPE,
        'id': str(uuid.uuid4()),
        'photos': []
    }

    if 'photos' in place:
        for photo in place['photos']:
            url = get_photo(photo).url
            location['photos'].append(url)
    print("Converted place:", place['name'])
    return location 

def convert_old_dynamo_place(p):
    location = {
            'name': p['name'],
#            'location': p['location'],
            'location': {
                'lat': p['location']['lat'],
                'lon': p['location']['lng']
                },
            'createdAt': time.time(),
            'type': p['type'],
            'id': p['id'],
        }
    if 'photos' in p:
        location['photos'] = p['photos']
#    if p['photos']: 
#        location['photos'].append(p['photos'][0]['link'])

    return location
