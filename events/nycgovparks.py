#  - https://www.nycgovparks.org/events/

import requests

from bs4 import BeautifulSoup
from datetime import datetime, time
from dateutil.parser import parse

from scripts import dyn_upload

url = 'https://www.nycgovparks.org'
page = '/events/free'
nextpage = '/p' # plus number (counting from 2)

PROD_TABLE = dyn_upload.PROD_EVENTS_TABLE
DEV_TABLE = dyn_upload.DEV_EVENTS_TABLE

def events(table):
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
            }

            if info['location_description'][:2] == 'at':
                info['location_description'] = info['location_description'][3:]

            if image and image.a:
                info['photos'] = [url + image.img.get('src')]

            description_page = BeautifulSoup(requests.get(info['website']).text, 'html.parser')
            info['description'] = description_page.find(class_='description').text

            if 'photos' not in info:
                i = description_page.find(class_='main_image')
                if i:
                    print('found main image')
                    i = i.find('a', href=True)
                    if i:
                        print('found a w/ href')
                        info['photos'] = [url + i.get('href')]
            if info['name'].lower() not in scraped_names and info['name'].lower() not in ddb_names:
                scraped_names.add(info['name'].lower())
                events.append(info)
            else:
                print('Already scraped:', info['name'])
    return events