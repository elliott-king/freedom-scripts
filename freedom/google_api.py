import os
import requests

from freedom.utils import Location

MAPS_API_KEY = os.environ['MAPS_API_KEY']
    
# It's good if the location_description is not the possessive form
def places_api_search_one(name: str):
    API_URL = 'https://maps.googleapis.com/maps/api/place/'
    OUTPUT = 'json'
    API_KEY = MAPS_API_KEY
    INPUTTYPE = 'textquery'
    MNH_BIAS = 'point:40.72986238308025,-74.02576541648762'

    query = name
    target = 'findplacefromtext'
    fields = {'geometry', 'name', 'type', 'place_id'}
    url = os.path.join(API_URL, target, OUTPUT)
    payload = {
                'locationbias': MNH_BIAS,
                'input': query,
                'inputtype': INPUTTYPE,
                'fields': ','.join(fields),
                'key': API_KEY
            }

    # Useful for debugging
    # from requests.models import PreparedRequest
    # req = PreparedRequest()
    # req.prepare_url(url, payload)
    # print(req.url)

    r = requests.get(url, params=payload)

    try:
        j = r.json()['candidates'][0] # first result probably correct
    except IndexError:
        raise TypeError('No location found: ', name)

    return Location(
        lat=j['geometry']['location']['lat'],
        lon=j['geometry']['location']['lng'],
    )