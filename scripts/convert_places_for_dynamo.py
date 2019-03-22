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

_TYPES = ['sculpture', 'public']
_PHOTO_MAXHEIGHT = 400

def get_photo(photo):
    url = 'https://maps.googleapis.com/maps/api/place/photo'
    payload = {
            'key': 'AIzaSyAZOtnRbMiYCyHWzI7EPhJylNYs-G573Uw',
            'maxheight': _PHOTO_MAXHEIGHT,
            'photoreference': photo['photo_reference']
    }
    r = requests.get(url, params=payload)
    return r


def convert_place_object(place):
    location = {
        'name': place['name'],
        'location': place['geometry']['location'],
        'date_added': time.time(),
        'types': _TYPES,
        'id': str(uuid.uuid4()),
        'photos': []
    }

    if 'photos' in place:
        for photo in place['photos']:
            photo_dict = {'link': get_photo(photo).url}
            if photo['html_attributions']:
                photo_dict['attribution'] = photo['html_attributions'][0]
            location['photos'].append(photo_dict)
    print("Converted place:", place['name'])
    return location 
