#  - https://www.nycgovparks.org/events/

import requests
import re

from bs4 import BeautifulSoup
from datetime import datetime, time, timedelta
from dateutil.parser import parse

from scripts import dyn_upload
from events import types

url = 'https://www.nycgovparks.org'
page = '/events/free'
nextpage = '/p' # plus number (counting from 2)


def events(table=dyn_upload.DEV_EVENTS_TABLE):
    events = []
    ddb_names = set([x['name'].lower() for x in dyn_upload.get_all_items_from_table(table)])
    scraped_names = set()
    for suffix in  [''] + [nextpage + str(x) for x in  range(2, 10)]:
        soup = BeautifulSoup(requests.get(url + page + suffix).text, 'html.parser')
        divs = soup.find_all('div', class_='event')

        for d in divs:
            body = d.find('div', class_='event_body')
            image = d.find('div', class_='span2')
            info = {
                'name': body.find(class_='event-title').text,
                'host': 'NYC Parks',
                'rsvp': False,
                'times': [
                    str(parse(body.p.find_all('strong')[0].text).time()),
                    str(parse(body.p.find_all('strong')[1].text).time())
                ],
                'dates': [str(parse(d.find('div', class_='date_graphic').text).date())],
                'website': url + body.find(class_='event-title').a.get('href'),
                'location_description': body.find(class_='location').text,
                'source': url,
                'types': [],
            }

            if info['location_description'][:2] == 'at':
                info['location_description'] = info['location_description'][3:]

            if image and image.a:
                info['photos'] = [url + image.img.get('src')]

            description_page = BeautifulSoup(requests.get(info['website']).text, 'html.parser')
            info['description'] = description_page.find(class_='description').text
            if 'rsvp' in info['description'].lower() or 'regist' in info['description'].lower():
                info['rsvp'] = True

            if 'photos' not in info:
                i = description_page.find(class_='main_image')
                if i:
                    i = i.find('a', href=True)
                    if i:
                        info['photos'] = [url + i.get('href')]

            types.add_type(info, 'athletics', ['athletics', 'exercise', 'fitness', 'physique', 'aerobics'])
            types.add_type(info, 'crafts', ['craft', 'coloring', 'knitting', 'sculpt', 'creative writing'])
            types.add_type(info, 'teen', ['teen', 'tween', 'homework'])
            types.add_type(info, 'family', ['toddler', 'preschool', 'baby', 'child', 'family', 'pre-school', 'families', 'kids'])
            types.add_type(info, 'nature', ['audobon', 'bird wa', 'nature', 'hike'])
            types.add_type(info, 'science', ['geolog', 'biolog'])
            types.add_type(info, 'advocacy', ['volunteer'])

            cat_header = None
            for h3 in description_page.find_all('h3'):
                if h3.text == 'Categories':
                    cat_header = h3
            if cat_header:
                categories_list = cat_header.next_sibling.text.split()
                # "Best for kids"
                exceptions = set(['art', 'games', 'education', 'senior'])
                for t in types.EVENT_TYPES:
                    if t not in exceptions:
                        for c in categories_list:
                            if t in c.lower():
                                if t not in info['types']:
                                    info['types'].append(t)

            dates_info = description_page.find(class_='alert')
            if dates_info:
                dates_info = dates_info.text
                has_named_days, is_weekdays, is_all_days = False, False, False
                m = re.search('between (.*) and (.*).', dates_info)
                if m:
                    start, end = m.groups()
                    start, end = parse(start).date(), parse(end).date()

                    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] # date.weekday is monday -> sunday
                    for d in days_of_week:
                        if d in dates_info.lower():
                            has_named_days = True # fine
                    if 'weekday' in dates_info:
                        is_weekdays = True
                    if 'every day' in dates_info:
                        is_all_days = True

                    if is_all_days: 
                        info['dates'] = [str(start + timedelta(days=x)) for x in range(0, (end - start).days + 1)]
                    elif is_weekdays or has_named_days:
                        info['dates'] = []
                        valid_days = []
                        if is_weekdays: 
                            valid_days = list(range(5))
                        else:
                            for i, d in enumerate(days_of_week):
                                if d in dates_info.lower():
                                    valid_days.append(i)
                        while start <= end:
                            if start.weekday() in valid_days:
                                info['dates'].append(str(start))
                            start += timedelta(1)

                    else:
                        print('Unable to parse dates_info')

            if info['name'].lower() not in scraped_names and info['name'].lower() not in ddb_names:
                scraped_names.add(info['name'].lower())
                events.append(info)
    return events