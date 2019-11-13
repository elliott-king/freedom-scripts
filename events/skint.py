# https://theskint.com/ongoing-events/

import requests
import datetime
import re
import json
import os

from bs4 import BeautifulSoup

def events():
    ret = []
    response = requests.get('https://theskint.com/ongoing-events/')

    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.find(class_='entry-content')
    entries = content.find_all('p')
    for entry in entries:
        if re.search('[fF]ree | pay-what-you-wish', entry.text):
            if entry.b.text and len(entry.b.text) > 3:
                
                d = {
                    'name': entry.b.text,
                    'website': entry.a.get('href'),
                    'description': entry.text[:-3],
                    'source': 'The Skint',
                    'rsvp': 'rsvp' in entry.text
                }

                stripped = strip_for_location_description(entry.text)
                description = location_description(stripped)
                if description:
                    d['location_description'] = description
                    d['host'] = description

                ret.append(d)

    return ret

def strip_for_location_description(s):
    end = len(s) + 1
    ending_substrings = ['$', 'free', 'pay-w']
    for sub in ending_substrings:
        if s.find(sub) != -1:
            end = min(end, s.find(sub))
            
    if s.find(':') != -1:
        start = s.find(':') + 1
    return s[start:end]

def location_description(s):
    matches = list(re.finditer('(\w+\s){1,5}\(.*?\)', s))
    if not matches: 
        return
    m = matches[-1].group()
    if m.find('at the ') != -1:
        m = m[m.find('at the ') + 7:]
    return m