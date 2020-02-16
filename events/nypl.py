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
                scrape_dates(info, eventpage)
                add_types(info)

                if not dyn_upload.is_uploaded(info, table) and not utils.in_prev_parsed_events(prev_events, info):
                    events.append(info)
                if 'dates' and 'host' in info:
                    utils.add_to_prev_events(prev_events, info)

    return events

def add_types(info):
    # TODO: Some types our users may not be initially interested in:
    # family, teen, education, senior, crafts, games, technology

    # TODO: if has type film, remove other types?

    utils.add_type(info, 'family', ['toddler', 'preschool', 'baby', 'babies', 'child', 'family', 'pre-school', 'families', 'kids', 'toys', 'story time', 'storytime', 'pre-k', 'open play', ' stem ', 'youngster', 'kidz', 'parent'])
    utils.add_type(info, 'music', ['jazz', 'music', 'song', 'concert', 'opera', 'baroque', 'fugue', 'choral'])
    utils.add_type(info, 'film', ['film', 'movie', 'matinee', 'cinema', 'screening'])
    utils.add_type(info, 'crafts', ['craft', 'coloring', 'knitting', 'sculpt', 'creative writing', 'sewing', 'materials', 'crochet', 'button', 'collage', 'felt ', 'perler', 'origami', 'supplies', 'beads', 'jewelry', 'create your own'])
    utils.add_type(info, 'games', ['jigsaw', 'puzzle', 'boardgame', 'video games', 'card game', 'dungeons & dragons', 'gaming', 'ps4', 'nintendo switch', 'xbox', 'game', 'crossword', ' uno', 'lego ', 'legos', 'mah jong', 'chess', 'wii', 'scrabble'])
    utils.add_type(info, 'advocacy', ['awareness', 'council member', 'citizenship'])
    utils.add_type(info, 'science', [' stem ', 'robot', ' steam '])
    utils.add_type(info, 'technology', [])
    utils.add_type(info, 'literature', ['literature', 'book discussion', 'book club', 'poem', 'poetry', 'reading and discussion', 'read and discuss'])
    # Tech things are really all classes: eg, learn CSS
    utils.add_type(info, 'education', ['learn how to', 'learn to', 'teach you', 'edit text', 'practice', 'research', 'job application', 'tutor', 'education', 'covers the basics', 'cover the basics', 'computer', 'css', 'html', 'technolog', 'blogging', 'edit text', 'tech issue', 'bilingual', 'photoshop', 'job seeker', 'resume build', 'application', 'microsoft', 'downloading', 'intro to', 'introduction to', 'your resume', 'job search', 'career', 'database', 'excel genius', 'census', 'classroom'])
    utils.add_type(info, 'health_medical', ['hygiene', 'mental health', 'first aid', 'disease', 'healthcare', 'health care', 'medical'])
    utils.add_type(info, 'senior', [' aging', 'seniors', 'aarp'])
    utils.add_type(info, 'athletics', ['athletics', 'exercise', 'fitness', 'physique', 'aerobics', 'sports', 'yoga'])
    utils.add_type(info, 'teen', ['teen', 'tween', 'homework', 'student', 'college', 'manga', 'anime', 'youth'])
    utils.add_type(info, 'history', ['history', 'historic'])
    utils.add_type(info, 'comedy', ['comed'])

    def check_age_range(start, end):
        start = int(start)
        if start < 11:
            if 'family' not in info['types']:
                info['types'].append('family')
        elif end:
            end = int(end)
            if end < 19:
                if 'teen' not in info['types']:
                    info['types'].append('teen')
        else:
            if 'teen' not in info['types']:
                info['types'].append('teen')


    # Attempt to parse an age range, if it exists
    if 'family' not in info['types'] and 'teen' not in info['types'] and 'description' in info:
        m = re.search(r'([0-9]+).+?([0-9]+)', info['description'])
        if m:
            check_age_range(m.group(1), m.group(2))
        else:
            m = re.search(r'ges ([0-9]+) and older', info['description'])
            if m:
                check_age_range(m.group(1), None)
            else:
                m = re.search(r'ges ([0-9]+) and up', info['description'])
                if m:
                    check_age_range(m.group(1), None)
                else:
                    m = re.search(r'ges ([0-9]+)[\s]?\+', info['description'])
                    if m:
                        check_age_range(m.group(1), None)
                    else:
                        m = re.search(r'ges ([0-9]+) &', info['description'])
                        if m:
                            check_age_range(m.group(1), None)


    # rsvp?
    info['rsvp'] = False
    for s in ['rsvp', 'regist', 'sign-up', 'ticket', 'reserve']:
        if s in info['name'].lower() or ('description' in info and s in info['description'].lower()):
            info['rsvp'] = True
    if 'description' in info and 'no registr' in info['description'].lower():
        info['rsvp'] = False

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
    for s in datestrs:
        try:
            d = parse(s)
            info['dates'].append(str(d.date()))
            info['times'].append(str(d.time()))
        except Exception as e:
            print("Unable to parse date for ", info['website'])
            print(e)

# Ease of doing user_input. TODO: should be sunsetted
def reddit_oriented(event):
    for t in ['family', 'teen', 'education', 'senior', 'crafts', 'games', 'technology']:
        if t in event['types']:
            return False
    return True