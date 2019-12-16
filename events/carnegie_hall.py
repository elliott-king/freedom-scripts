# https://www.carnegiehall.org/Events/Citywide

import requests
import json
import os

from bs4 import BeautifulSoup
from datetime import datetime, time
import time as timestamp

headers = {
    'authority': 'q0tmlopf1j-dsn.algolia.net',
    'accept': 'application/json',
    'origin': 'https://www.carnegiehall.org',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'referer': 'https://www.carnegiehall.org/Events/Citywide',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
}

params = (
    ('x-algolia-agent', 'Algolia for vanilla JavaScript (lite) 3.27.0;JS Helper 2.25.1'),
    ('x-algolia-application-id', 'Q0TMLOPF1J'),
    ('x-algolia-api-key', '30a0c84a152d179ea8aa1a7a59374d08'),
)

t = str(int(timestamp.time()))

# Used to be 100 instead of 000
data = ('{"requests":[{"indexName":"sitecore-events","params":"query=&hitsPerPage=10&page=0&facets=%5B%22eventtype%22%2C%22seasonnumber%22%2C%22facilityfacet%22%2C%22genre%22%2C%22instrument%22%5D&tagFilters=&facetFilters=%5B%22eventtype%3ACarnegie%20Hall%20Presents%22%2C%22eventtype%3AFree%20Events%22%2C%22facilityfacet%3AOffsite%22%2C%5B%22facilityfacet%3AOffsite%22%5D%5D&numericFilters=%5B%22'
    'startdate%3E' + t + '000%22%5D"},{"indexName":"sitecore-events","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=genre&numericFilters=%5B%22'
    'startdate%3E' + t + '000%22%5D&facetFilters=%5B%22eventtype%3ACarnegie%20Hall%20Presents%22%2C%22eventtype%3AFree%20Events%22%2C%22facilityfacet%3AOffsite%22%2C%5B%22facilityfacet%3AOffsite%22%5D%5D"},{"indexName":"sitecore-events","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=facilityfacet&numericFilters=%5B%22'
    'startdate%3E' + t + '000%22%5D&facetFilters=%5B%22eventtype%3ACarnegie%20Hall%20Presents%22%2C%22eventtype%3AFree%20Events%22%2C%22facilityfacet%3AOffsite%22%5D"},{"indexName":"sitecore-events","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=instrument&numericFilters=%5B%22'
    'startdate%3E' + t + '000%22%5D&facetFilters=%5B%22eventtype%3ACarnegie%20Hall%20Presents%22%2C%22eventtype%3AFree%20Events%22%2C%22facilityfacet%3AOffsite%22%2C%5B%22facilityfacet%3AOffsite%22%5D%5D"}]}')

def eval():
    return requests.post('https://q0tmlopf1j-dsn.algolia.net/1/indexes/*/queries', headers=headers, params=params, data=data)

def events():
    response = eval()
    i = []
    for hit in response.json()['results'][0]['hits']:

        info = {
            'name': hit['title'].replace('<BR>', ' '),
            # TODO: datetime is just set as UTC..
            'dates': [str(datetime.strptime(hit['date'], '%A, %b %d, %Y').date())],
            'times': [str(timeformat(hit['time']))],
            'website': 'https://carnegiehall.org' + hit['url'],
            'photos': [hit['image']['src']],
            'host': 'Carnegie Hall',
            'source': 'Carnegie Hall Citywide',
            'location_description': hit['facility'],
            'types': ['music'],
            'rsvp': True # TODO: currently assuming the worst
        }

        more_info_response = requests.get(info['website'])
        soup = BeautifulSoup(more_info_response.text, 'html.parser')

        location_text = soup.find_all(class_='ch-event-facilityNotes')[0].text
        description_text = soup.find_all(class_='ch-page-hero-block__content')[0].text

        location_text = ' '.join(location_text.strip().split('\n')[2:-1])
        description_text = description_text.strip()
        info['description'] = description_text
        i.append(info)
    return i

def timeformat(t):
    hour, minute, post = 0,0,'AM'
    check = t[1]
    if check == ' ' or check == ':':
        hour = int(t[0])
        post = t[-2:]
        if check == ':':
            minute = int(t[2:4])
    else:
        check = t[2]
        hour = int(t[:2])
        post = t[-2:]
        if check == ':':
            minute = int(t[3:5])
    if hour == 12:
        hour = 0
    if post == 'PM':
        hour += 12
    return time(hour=hour, minute=minute)