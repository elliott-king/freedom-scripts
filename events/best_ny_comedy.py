# https://bestnewyorkcomedy.com/

import requests
import datetime
import re

from bs4 import BeautifulSoup
from dateutil.parser import parse

# When overall page was last updated
def updated(soup):
    return parse(soup.small.text)

def entry(soup):
    return soup.find(class_='entry')

def freebies(entry): 
    freebies = []
    for p in entry.find_all('p'):
        if 'Free!' in p.text:
            freebies.append(p)
    return freebies

def extract(freebie):
    info = {
        'source': 'https://bestnewyorkcomedy.com',
        'types': ['comedy'],
        'photos': [freebie.img['data-orig-file']],
        'description': freebie.text,
        'rsvp': 'rsvp' in freebie.text,
        'times': [re.search(r'[\d]:[\d][\d] [AaPp][Mm]', freebie.text).group()]
    }

    links = freebie.find_all('a')
    for i in range(len(links)):
        l = links[i]
        if l.b:
            info['name'] = l.b.text
            info['website'] = l['href']
        if 'href' in l:
            if 'google' in l['href'] and 'maps' in l['href'] and 'place' in l['href']:
                info['location_description'] = l.text
                info['host'] = links[i-1].text

    bolded = freebie.find_all('b')
    for b in bolded:
        try:
            info['dates'] = [str(parse(b.text[:-1]).date())]
        except ValueError:
            pass
    if 'dates' not in info:
        print('Unable to find date for event', info['name'])
    
    return info

def events():
    soup = BeautifulSoup(requests.get('https://bestnewyorkcomedy.com/').text, 'html.parser')
    most_recent = entry(soup)
    return [extract(i) for i in freebies(most_recent)]
