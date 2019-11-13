import pprint
import requests
import json
import os

from dateutil.parser import parse
from datetime import datetime

import events_upload

API_URL = 'https://maps.googleapis.com/maps/api/place/'
OUTPUT = 'json'
# Maybe store elsewhere on disk
API_KEY = 'AIzaSyCZ21RlCa8IVwxR-58b8fTgUXn_a4UYhbc'
INPUTTYPE = 'textquery'
mnh_bias = 'point:40.72986238308025,-74.02576541648762'

multi_fields = ['types', 'dates', 'times']

title_fields = [
    'name', 'host', 'source', 'location_description'
]

single_fields = [
    'description','website', 'rsvp'
    # Omit 'location', need Google for that.
    # omit photos?
]

# should create new dict
def request_input(d):
    print('=' * 40)
    missing = []
    for f in (single_fields + title_fields):
        if f not in d:
            missing.append(f)
            d[f] = None
    for f in multi_fields:
        if f not in d:
            missing.append(f)
            d[f] = []
    print('Expected but did not find:', missing)
    print('Text:')
    print(d['description'])

    # Accept user input for singleton fields
    for f in d:
        if f not in multi_fields:
            print(f.upper(), ':', ' ' * (20 - len(f)), d[f])
            new = input('If applicable, new value:\n')
            if new and new != 'yes' and new  != 'y' and new != 'Y' and new != 'Yes':
                d[f] = new
            if f in title_fields:
                d[f] = d[f].title()

    apply_dates(d)
    apply_times(d)
    apply_types(d)

    if 'location' not in d:
        d['location'] = search_one(d['location_description'])

    pprint.pprint(d)
    upload = input('Upload (y/N)? ')
    if upload in ['y', 'Y', 'yes', 'Yes']:
        events_upload.add_items_to_table(events_upload.EVENTS_TABLE, [d])
    else:
        print('Did not upload')
    
# It's good if the location_description is not the possessive form
def search_one(name):
    query = name
    target = 'findplacefromtext'
    fields = {'geometry/location', 'name', 'types', 'place_id'}
    url = os.path.join(API_URL, target, OUTPUT)
    payload = {
                'locationbias': mnh_bias,
                'input': query,
                'inputtype': INPUTTYPE,
                'fields': ','.join(fields),
                'key': API_KEY
            }
    r = requests.get(url, params=payload)

    j = r.json()['candidates'][0] # first result probably correct
    
    location = {
        'lat': j['geometry']['location']['lat'],
        'lon': j['geometry']['location']['lng']
    }
    return location

def apply_times(d):
    print('times:', d['times'])
    times = []
    while(True):
        new = input('Enter a time, or refuse: ')
        if new and new != 'yes' and new != 'y' and new != 'Y' and new != 'Yes':
            times.append(str(parse(new).time()))
        else:
            break
    if times:
        d['times'] = times
    

def apply_dates(d):
    print('dates:', d['dates'])
    dates = []
    while(True):
        new = input('Enter a date, or refuse: ')
        if new and new != 'yes' and new != 'y' and new != 'Y' and new != 'Yes':
            dates.append(str(parse(new).date())) # user should write in year, if it is next year
        else:
            break
    if dates:
        d['dates'] = dates

def apply_types(d):
    print('types:', d['types'])
    types = []
    while(True):
        new = input('Enter a type, or refuse: ')
        if new and new != 'yes' and new != 'y' and new != 'Y' and new != 'Yes':
            types.append(new)
        else:
            break
    if types:
        d['types'] = types