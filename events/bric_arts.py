# https://www.bricartsmedia.org/events-performances

import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse
from collections import defaultdict

from scripts import dyn_upload
from events import utils

base = 'https://www.bricartsmedia.org'
page = '/events-performances'

# TODO: some events have multiple dates, we are only currently parsing the first!

def events(table=dyn_upload.DEV_EVENTS_TABLE):
    soup = BeautifulSoup(requests.get(base + page).text, 'html.parser')
    prev_events = defaultdict(list)
    events = []
    for article in soup.find_all(class_='node-event'):
        event = {
            'name': article.find(class_='listing-title').text,
            'website': base + article.find(class_='listing-title').a.get('href'),
            'photos': article.find('img', class_='lazyload').get('src'),
            'source': 'BRIC',
            'rsvp': False,
        }
        if article.find(class_='listing-body').text:
            event['description'] = article.find(class_='listing-body').text

        event_soup = BeautifulSoup(requests.get(event['website']).text, 'html.parser')
        for right_item in event_soup.find_all('div', class_='intro-banner-right-item'):
            if 'Date' in right_item.text:
                d = right_item.span.text.strip().replace('•', '').replace('|', '')
                d = d.split('-')[0]
                if 'am' not in d.lower() and 'pm' not in d.lower():
                    # TODO: should really check what time it was
                    # But I am lazy
                    d += 'pm'
                d = parse(d)
                event['dates'] = [str(d.date())]
                event['times'] = [str(d.time())]
            if 'Cost' in right_item.text:
                if 'free' not in right_item.text.lower():
                    continue
                if 'rsvp' in right_item.text.lower() or 'regist' in right_item.text.lower():
                    event['rsvp'] = True
            if 'Location' in right_item.text:
                event['host'] = right_item.strong.text
                event['location_description'] = right_item.find(class_='thoroughfare').text + ' ' + right_item.find(class_='locality-block').text
        if 'description' not in event or not event['description']:
            event['description'] = event_soup.find('div', class_='event-image-contain').find_next_sibling().text
        for link in event_soup.find_all('a'):
            if 'rsvp' in link.text.lower() or 'regist' in link.text.lower():
                event['rsvp'] = True

        if not dyn_upload.is_uploaded(event, table) and not utils.in_prev_parsed_events(prev_events, event):
            events.append(event)
            utils.add_to_prev_events(prev_events, event)
    return events