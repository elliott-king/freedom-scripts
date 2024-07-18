# https://hellskitchen.ucbtheatre.com/schedule

import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse

from scripts import dyn_upload

base = 'https://hellskitchen.ucbtheatre.com'
url = base + '/schedule'

def events(table=dyn_upload.DEV_EVENTS_TABLE):
    events = []

    cal = BeautifulSoup(requests.get(url).text, 'html.parser')
    for day in cal.find_all('td'):
        for cell in day.find_all('a', class_='calendar_link'):
            cost = cell.find('span', class_='pull-right').text
            if 'free' in cost.lower():
                info = {
                    'dates': [str(parse(day.find('div', class_='day_title').div.text).date())],
                    'website': base + cell.get('href'),
                    'location_description': '555 W 42nd Street, New York, NY',
                    'rsvp': False, # They only sell tickets for charged events, it seems
                    'source': base,
                    'name': cell.find(class_='performance_title').text,
                    'host': 'UCB Theatre Hells Kitchen',
                    'types': ['comedy']
                }
                timestr = cell.find('span', class_='pull-left').text
                if 'midnight' in timestr.lower():
                    info['times'] = ['23:59']
                else:
                    info['times'] = [str(parse(timestr).time())]

                site = BeautifulSoup(requests.get(info['website']).text, 'html.parser')
                content = site.find('div', id='content_container').find('div', class_='clearfix')

                strs = list(content.stripped_strings)
                if 'Cast' in strs:
                    i = len(strs) - strs[::-1].index('Cast')
                    strs = strs[i:]
                elif 'Host' in strs:
                    i = len(strs) - strs[::-1].index('Host')
                    strs = strs[i:]
                else:
                    print('neither "cast" nor "host" in website')
                info['description'] = " ".join(strs)

                # info['description'] = max(list(content.stripped_strings))
                if content.find('img', class_='img-thumbnail'):
                    info['photos'] = [content.find('img', class_='img-thumbnail').get('src')]

                if not dyn_upload.is_uploaded(info, table):
                    events.append(info)
    return events
