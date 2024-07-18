# https://www.bricartsmedia.org/events-performances

import requests 

from bs4 import BeautifulSoup 
from dateutil.parser import parse

from scripts import dyn_upload

base = "https://www.bricartsmedia.org"
api = "/api/events"

def events(table=dyn_upload.DEV_EVENTS_TABLE):
  events = []
  events_json = requests.get(base + api).json()['events']
  for i, json in enumerate(events_json):
    date = parse(json['date']).date().isoformat()
    # the actual event always seems to be the only element in a subarray
    json = json['events'][0]
    if 'free' not in json['cost'].lower():
      continue
    event = {
      'name': json['title'],
      'website': json['link'],
      'dates': [date],
      # WOW this is cheap. Too lazy to immediately fix this
      'times': [parse(json['time'][:2] + ':' + json['time'][2:]).time().isoformat()],
      'rsvp': True,
      'source': 'BRIC',
      'description': BeautifulSoup(json['desc'], 'html.parser').text.strip(),
      'host': json['location'] if json['location'] else 'BRIC',
      # TODO: quarantine only
      'location_description': 'Brooklyn',
    }
    photo_tag = BeautifulSoup(json['image'], 'html.parser').img
    if photo_tag:
      event['photos'] = photo_tag['src']
    events.append(event)
  return events