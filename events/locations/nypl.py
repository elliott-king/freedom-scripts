# https://www.nypl.org/events/calendar

import requests
import re 
import os

from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import date
from collections import defaultdict

from scripts import dyn_upload
from events import utils
from events import types

url = 'https://www.nypl.org'
page = '/events/calendar'
nextpage = '?page=' # plus number (counting from 2)

location_api = 'https://refinery.nypl.org/api/nypl/locations/v1.0/locations/'

def events(table=dyn_upload.DEV_EVENTS_TABLE):
    events = []
    prev_events = defaultdict(list)
    for suffix in [''] + [nextpage + str(x) for x in range(2, 60)]:
        print('Now looking at page', suffix)
        searchpage = BeautifulSoup(requests.get(url + page + suffix).text, 'html.parser')
        rows = searchpage.find_all('tr', class_='col-4')
        for r in rows:
            # The website is not correctly formatted, I think..? The <table> tags do not match what is shown in
            # FF/Chrome DOM. Assumedly, some weird things are happening in the browser display.

            # If the title/description section has a header title (eg EARLY LITERACY.... Toddler and Preschool Story Time)
            # Then the header title will be in the <tr> but the actual title will be in its own <a> and description in
            # its own following <div>
            blurb = r.find(class_='event-title')
            if blurb:
                info = {
                    'source': url,
                    'dates': [],
                    'types': ['library'],
                    'times': [],
                }

                searchpage_event_date = None
                if r.find(class_='event-time'):
                    searchpage_event_date = r.find(class_='event-time').text.replace("@", "at")
                    if 'Today' in searchpage_event_date:
                        searchpage_event_date = str(date.today())
                    else:
                        if 'noon' in searchpage_event_date:
                            searchpage_event_date = re.search('(.*) noon', searchpage_event_date).group(1)
                        searchpage_event_date = str(parse(searchpage_event_date).date())

                # has channel title, and therefore the channel title is the end of the <tr>
                # this one behaves so, so weirdly
                if blurb.find(class_='channel-title'):
                    # Using the nypl event subheader (channel-title) to infer types
                    ct = blurb.find(class_='channel-title').text.lower()
                    if 'early literacy' in ct:
                        info['types'].append('family')
                    if 'techconnect' in ct or 'microsoft' in ct or 'tax prep':
                        info['types'].append('education')
                    if 'book discuss' in ct:
                        info['types'].append('literature')
                    # TODO: if next div ('event-audience') contains 'children' -> make types = ['family']

                    try:
                        while not blurb.next_sibling:
                            blurb = blurb.findParent()
                        a = blurb.next_sibling
                        info['name'] = a.text
                        info['website'] = url + a.get('href')
                        while not a.next_sibling:
                            a = a.findParent()
                        next = a.next_sibling
                        if 'description' in next.get('class', None):
                            info['description'] = next.text
                            while not next.next_sibling:
                                next = next.findParent()
                            next = next.next_sibling
                        if 'event-location' in next.get('class', None):
                            info['host'] = next.text
                    except Exception:
                        print('issue with event', info['name'], 'on page', url + page + suffix)

                # Otherwise, will behave mostly normally
                else:
                    info['name'] = r.a.text
                    info['host'] = r.find(class_='event-location').text
                    info['website'] = url + r.a.get('href')
                if r.find('div', class_='description'):
                    info['description'] = r.find('div', class_='description').text

                if utils.in_prev_parsed_events(prev_events, info, onetime_date=searchpage_event_date):
                    continue
                
                eventpage = BeautifulSoup(requests.get(info['website']).text, 'html.parser')
                
                # https://stackoverflow.com/questions/3925096
                if eventpage.find('div', class_='event-location'):
                    if eventpage.find('div', class_='event-location').a:
                        libraryUrl = os.path.join(
                            location_api, 
                            os.path.basename(os.path.normpath(
                                eventpage.find('div', class_='event-location').a.get('href'))))
                        try:
                            library = requests.get(libraryUrl).json()
                            if 'location' in library:
                                library = library['location']
                                info['location_description'] = ''.join([
                                    library['street_address'], ', ',
                                    library['locality'], ', ',
                                    library['region'],
                                ])
                                if 'host' not in info:
                                    info['host'] = library['name']
                            else:
                                print('No api location json for library', info['website'])
                        except Exception as e:
                            print('Could not access api for library:', eventpage.find('div', class_='event-location').a.text)
                if not scrape_dates(info, eventpage):
                    continue
                types.add_types(info)
                types.add_rsvp(info)

                if not dyn_upload.is_uploaded(info, table) and not utils.in_prev_parsed_events(prev_events, info):
                    events.append(info)
                if 'dates' and 'host' in info:
                    utils.add_to_prev_events(prev_events, info)

    return events

def scrape_dates(info, eventpage):
    deets = eventpage.find('div', class_='event-details')

    # dates can be single object (div), ul of dates, or single obj + ul (different format)

    def truncate_date_str(s):
        stripped_datestr = s
        if '-' in s:
            stripped_datestr = re.search('(.*) -', s).group(1)

        if "noon" in stripped_datestr.lower():
            stripped_datestr = re.search('(.*) noon', stripped_datestr).group(1) + ' 12p.m.'
        if "a.m." not in stripped_datestr.lower() and "p.m." not in stripped_datestr.lower():
            if "a.m." in s.lower():
                stripped_datestr += "a.m."
            else:
                stripped_datestr += "p.m."
        return stripped_datestr
    
    datestrs = []
    if deets:
        date = deets.find(class_='program-date')
        if date.name == 'div':
            datestrs.append(truncate_date_str(date.text.strip()))
            if eventpage.find('div', class_='program-dates-upcoming'):
                for li in eventpage.find('div', class_='program-dates-upcoming').find_all('li'):
                    datestrs.append(truncate_date_str(li.text))
        elif date.name == 'ul':
            for li in date.find_all('li'):
                datestrs.append(truncate_date_str(li.text))
        else:
            print('ERROR getting date, not type of div or ul')

    # TODO: handle more than one time?
    cancellations = 0
    for s in datestrs:
        if 'cancel' in s.lower():
            cancellations += 1
        try:
            d = parse(s)
            info['dates'].append(str(d.date()))
            info['times'].append(str(d.time()))
        except Exception as e:
            print("Unable to parse date for ", info['website'])
            print(e)
    
    if cancellations >= len(datestrs):
        print('Event cancelled: ', info['name'])
        return False 
    return True

# Ease of doing user_input. TODO: should be sunsetted
def reddit_oriented(event):
    for t in ['family', 'teen', 'education', 'senior', 'crafts', 'games', 'technology']:
        if t in event['types']:
            return False
    return True