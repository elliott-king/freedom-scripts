#  - https://www.nycgovparks.org/events/

import requests

from bs4 import BeautifulSoup
from datetime import datetime, time
from dateutil.parser import parse

url = 'https://www.nycgovparks.org'
page = '/events/free'
nextpage = '/p' # plus number (counting from 2)

def events():
    events = []
    for suffix in  [''] + [nextpage + str(x) for x in  range(2, 4)]:
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
                info['photos']: [image.a.get('href')]

            description_page = BeautifulSoup(requests.get(info['website']).text, 'html.parser')
            info['description'] = description_page.find(class_='description').text
            events.append(info)
    return events