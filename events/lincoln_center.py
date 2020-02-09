# http://www.lincolncenter.org/free

import requests
import json
import os

from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import datetime, time
import time as timestamp

from scripts import dyn_upload

base = 'http://www.lincolncenter.org'
page = '/free'

# div can have data-tags = music, free, family, exhibition (not a concert), opera, theater

def events(table=dyn_upload.DEV_EVENTS_TABLE):
    soup = BeautifulSoup(requests.get(base + page).text, 'html.parser')
    events = []
    for card in soup.find_all('div', class_='card'):
        event = {
            'name': card.find(class_='card-text').h1.text,
            'source': 'The Lincoln Center',
            'photos': [card.find(class_='card-img').img.get('src')],
            'website': base + card.find(class_='card-img').a.get('href'),
            'host': card.find(class_='event-venue').text,
            'rsvp': False, # dependent on event page
            'types': [],
            'dates': [],
            'times': [],
        }

        tags = card.get('data-tags').lower().split()
        if 'free' not in tags:
            print(event['name'], 'is not free', event['website'])
            continue
        if 'music'in tags or 'opera' in tags:
            event['types'].append('music')
        if 'family' in tags:
            event['types'].append('family')
        if 'theater' in tags:
            event['types'].append('theater')

        event_soup = BeautifulSoup(requests.get(event['website']).text, 'html.parser')
        event['description'] = event_soup.find(class_='event-left').find(class_='text-block').text.strip()
        if event_soup.find('a', class_='ticket-button'):
            event['rsvp'] = True

        datestrs = []
        if event_soup.find('div', class_='event-perfs-cont'): # there is a list of datestrs... (divs)
            for event_perf in event_soup.find('div', class_='event-perfs-cont').find_all('div', class_='event-perf'):
                datestrs.append(event_perf.span.text.strip())
        else:
            datestr = event_soup.find(class_='event-right').find(class_='event-date').text.strip()
            # Hard to parse, and they don't contain times...?
            # These repeating Julliard events don't seem to be shown correctly
            # TODO: maybe we can come back in a few months & they will be fixed
            # Also some of them are exhibitions
            if '-' in datestr or '–' in datestr: 
                print('Not parsing event', event['name'], 'because it has no clear times:', event['website'])
                continue
            datestrs = [datestr]
        for ds in datestrs:
            try:
                dt = parse(ds)
                event['dates'].append(str(dt.date()))
                event['times'].append(str(dt.time()))
            except Exception as e:
                print('For event:', event['name'], 'unable to parse datetime', dt, 'at', event['website']) 
        # See above. If we can't parse anything, skip
        if len(event['dates']) < 1:
            continue   

        # Some oddly dead links
        venue_url = card.find(class_='event-venue').a.get('href')
        if 'Public Library' in event['host'] and 'Performing Arts' in event['host']:
            event['location_description'] = '40 Lincoln Center Plaza, New York, NY'
        else:
            if 'Morse' in event['host']:
                venue_url = 'https://lincolncenter.org/venue/morse-hall'
            venue_soup = BeautifulSoup(requests.get(venue_url).text, 'html.parser')
            event['location_description'] = venue_soup.find(class_='ed-show-tell--data__item location').find(class_='data-item-copy').text + ', New York, NY'

        if not dyn_upload.is_uploaded(event, table):
            events.append(event)
    return events
