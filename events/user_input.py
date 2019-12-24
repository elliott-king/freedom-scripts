import pprint
import requests
import json
import os

from dateutil.parser import parse
from datetime import datetime, timedelta
from titlecase import titlecase

from scripts import dyn_upload

API_URL = 'https://maps.googleapis.com/maps/api/place/'
OUTPUT = 'json'
# Maybe store elsewhere on disk
API_KEY = 'AIzaSyCZ21RlCa8IVwxR-58b8fTgUXn_a4UYhbc'
INPUTTYPE = 'textquery'
mnh_bias = 'point:40.72986238308025,-74.02576541648762'

multi_fields = ['types', 'dates', 'times']

title_fields = [
    'name', 'host', 'location_description'
]

single_fields = [
    'website', 'description', 'rsvp', 'source'
    # Omit 'location', need Google for that.
    # omit photos?
]

# should create new dict
def request_input(d):
    try:
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
        if 'website' in d:
            print(d['website'], '\n')

        # Accept user input for singleton fields
        for f in d:
            if f not in multi_fields:
                print(f.upper(), ':', ' ' * (20 - len(f)), d[f])
                new = input('If applicable, new value:\n')
                if new and new != 'yes' and new  != 'y' and new != 'Y' and new != 'Yes':
                    d[f] = new
                if f in title_fields:
                    d[f] = titlecase(d[f])

        apply_dates(d)
        apply_times(d)
        apply_types(d)

        if 'location' not in d:
            d['location'] = search_one(d['location_description'])

        pprint.pprint(d)
    
        if not check_filled(d):
            print ('Not uploading.')
            return
        upload = input('Upload (Y/n)? ')
        if upload in ['n', 'N', 'no', 'No', 'NO']:
            print('Did not upload')
        else:
            # TODO: should choose table
            dyn_upload.add_items_to_table(dyn_upload.DEV_EVENTS_TABLE, dyn_upload.DEV_PHOTOS_TABLE, [d])
        
    except Exception as e:
        print('Issue with information:', e)
        print('Not uploading.')
    
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

    try:
        j = r.json()['candidates'][0] # first result probably correct
    except IndexError:
        raise TypeError('No location found: ', name)
    
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

            # date range should be user-formatted start,end
            if ',' in new:
                [s,e] = new.split(',')
                print(s,e)
                s = parse(s).date()
                e = parse(e).date()
                print(s,e)
                arr = [str(s + timedelta(days=x)) for x in range(0, (e - s).days + 1)]
                print(arr)
                dates += arr
            else:
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

def check_filled(d):
    for f in multi_fields + title_fields + single_fields:
        if f != 'times' and f != 'rsvp':
            if not d[f]:
                print('Expecting at least one value for field: ' + f)
                return False
    return True