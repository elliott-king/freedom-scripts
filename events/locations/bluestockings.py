# bluestockings.com/calendar

import requests
import re

from bs4 import BeautifulSoup
from dateutil.parser import parse

from scripts import dyn_upload
from events import types

url = 'https://bluestockings.com/calendar'

# can be extended with action~agenda/exact_date~1-1-2020 etc

def events(table=dyn_upload.DEV_EVENTS_TABLE):
    ddb_names = dict([(x['name'].lower(),x['dates']) for x in dyn_upload.get_all_items_from_table(table)])
    events = []
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    sections = soup.find_all("div", class_="ai1ec-event")
    for sec in sections:
        if sec.find(class_="ai1ec-read-more"): # sometimes doesn't find this? not sure why
            info = {
                'name': sec.find(class_="ai1ec-event-title").text.strip(),
                'website': sec.find(class_="ai1ec-read-more").get('href').strip(),
                'location_description': "172 Allen St, New York, NY",
                'host': "Bluestockings",
                'rsvp': True, # TODO: update scraper for this
                'description': sec.find(class_="ai1ec-event-description").text,
                'source': 'bluestockings.com',
            }
            e_soup = BeautifulSoup(requests.get(info['website']).text, 'html.parser')

            # TODO: some events are repeating: we should check if they have the same dates
            info['description'] = ""
            for p in e_soup.find("div", class_="entry-content").find_all("p"):
                info['description'] += p.text + '\n'
            # just doing start time, meh
            e_soup.find()
            d, t = re.search("(.*) @ (.*) –", e_soup.find("div", class_="dt-duration").text).groups()
            info['dates'] = [str(parse(d).date())]
            info['times'] = [str(parse(t).time())]
            info['types'] = types.types(info['description'])

            if not dyn_upload.is_uploaded(info, table):
                events.append(info)
    return events