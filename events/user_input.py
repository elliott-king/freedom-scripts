import pprint
import requests
import json
import os
import traceback

from dateutil.parser import parse
from datetime import datetime, timedelta
from titlecase import titlecase
from collections import defaultdict

from scripts import dyn_upload

multi_fields = ['types', 'dates', 'times']

title_fields = [
    'name', 'host', 'location_description'
]

single_fields = [
    'website', 'description', 'rsvp', 'source'
    # Omit 'location', need Google for that.
    # omit photos?
]

IN_QUARANTINE = True
SKIP_FAMILY_EVENTS = True

class SkipEventError(Exception):
    """Signify that user would like to skip this event."""
    def __init__(self, message):
        self.message = message

def request_multiple(events):
    events = squash_events(events)
    for i, e in enumerate(events):
        print('on item', i, 'of', len(events))
        request_input(e)

# should create new dict
def request_input(d):
    print('=' * 40)
    if d['website'] and len(d['website']) < 6:
        # Throw out garbage
        del d['website']
    if check_canceled(d):
        return
    display_missing(d)
    if 'id' in d:
        del d['id']
    if SKIP_FAMILY_EVENTS:
        if not reddit_oriented(d):
            return
    if IN_QUARANTINE:
        if not d['location_description']:
            d['location_description'] = 'Manhattan'
    try:
        display_info(d)
        singleton_fields(d)

        apply_dates(d)
        apply_times(d)
        apply_types(d)

        if 'location' not in d:
            d['location'] = search_one(d['location_description'])

        pprint.pprint(d)

        if not check_filled(d):
            print ('Not uploading.')
            return
        if 'website' in d and 'http' not in d['website']:
            d['website'] = 'http://' + d['website']
        upload = get_user_input('Upload (Y/n)? ')
        if upload in ['n', 'N', 'no', 'No', 'NO']:
            print('Did not upload')
        else:
            # TODO: should choose table
            dyn_upload.add_items_to_table(dyn_upload.DEV_EVENTS_TABLE, dyn_upload.DEV_PHOTOS_TABLE, [d])
    
    except SkipEventError:
        print('Skipping this event')
    except Exception:
        print(traceback.format_exc())
        print('Issue with information, NOT UPLOADING')

def display_missing(d):
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

def check_canceled(d):
    for field in ['name', 'description']:
        if d[field]:
            if 'canceled' in d[field].lower() or 'cancelled' in d[field].lower():
                print("Event canceled:", d['name'])
                return True
    return False

def display_info(d):
    print('Text:')
    print(d['description'])
    if 'website' in d:
        print(d['website'], '\n')

def singleton_fields(d):
    for f in d:
        if f not in multi_fields:
            print(f.upper(), ':', ' ' * (20 - len(f)), d[f])
            new = get_user_input('If applicable, new value:\n')
            if new and new != 'yes' and new  != 'y' and new != 'Y' and new != 'Yes':
                d[f] = new
                if f.lower() == 'rsvp':
                    d[f] = d[f] == 'True'
            if f in title_fields:
                d[f] = titlecase(d[f])
    
# It's good if the location_description is not the possessive form
def search_one(name):
    API_URL = 'https://maps.googleapis.com/maps/api/place/'
    OUTPUT = 'json'
    API_KEY = 'AIzaSyCZ21RlCa8IVwxR-58b8fTgUXn_a4UYhbc'
    INPUTTYPE = 'textquery'
    MNH_BIAS = 'point:40.72986238308025,-74.02576541648762'

    query = name
    target = 'findplacefromtext'
    fields = {'geometry/location', 'name', 'types', 'place_id'}
    url = os.path.join(API_URL, target, OUTPUT)
    payload = {
                'locationbias': MNH_BIAS,
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
        new = get_user_input('Enter a time, or refuse: ')
        if new and new != 'yes' and new != 'y' and new != 'Y' and new != 'Yes':
            times.append(str(parse(new).time()))
        else:
            break
    if times:
        d['times'] = times
    

def apply_dates(d):
    # TODO: some nypl events have multiple times w/in one day
    d['dates'] = list(set(d['dates']))
    print('dates:', d['dates'])
    dates = []
    while(True):
        new = get_user_input('Enter a date, or refuse: ')
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
        new = get_user_input('Enter a type, or refuse: ')
        if new and new != 'yes' and new != 'y' and new != 'Y' and new != 'Yes':
            types.append(new)
        else:
            break
    if types:
        d['types'] = types

def check_filled(d):
    for f in multi_fields + title_fields + single_fields:
        if f not in['rsvp', 'times', 'source', 'website']:
            if f not in d or not d[f]:
                print('Expecting at least one value for field: ' + f)
                return False
    return True

def get_user_input(s):
    i = input(s)
    if i and i == 'skip':
        raise SkipEventError('Skip this event.')
    return i

# In the interest of making my work simpler, and making this more presentable where I am putting up
# the events (namely reddit), we can identify the family-oriented events and set them aside.
def reddit_oriented(event):
    for t in ['family', 'teen', 'senior', 'crafts', 'games', 'technology']: # education
        if t in event['types']:
            print("Event is family event, has type:", t)
            return False
    return True

# events that have the same name should be merged, with their dates & times added together
# after quarantine, may be good to enforce that events also have the same location_description
def squash_events(events):
    ret = []
    events_by_name = defaultdict(list)
    for e in events:
        events_by_name[e['name']].append(e)
    
    for _event_name, list_by_name in events_by_name.items():
        if len(list_by_name) == 1:
            ret.append(list_by_name[0])
            continue
        combined_event = list_by_name[0]
        for shared_event in list_by_name[1:]:
            combined_event['dates'] = list(set(combined_event['dates'] + shared_event['dates']))
            combined_event['times'] += shared_event['times']
        ret.append(combined_event)
    return ret