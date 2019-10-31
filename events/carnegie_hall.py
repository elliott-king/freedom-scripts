# https://www.carnegiehall.org/Events/Citywide

import requests
import json
import os

from bs4 import BeautifulSoup

API_URL = 'https://maps.googleapis.com/maps/api/place/'
OUTPUT = 'json'
# DO NOT SUBMIT: cannot make git repo public now.
# Maybe store elsewhere on disk
API_KEY = 'AIzaSyCZ21RlCa8IVwxR-58b8fTgUXn_a4UYhbc'
INPUTTYPE = 'textquery'
mnh_bias = 'rectangle:40.72986238308025,-74.02576541648762|40.72986238308025,-74.02576541648762'

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

data = '{"requests":[{"indexName":"sitecore-events","params":"query=&hitsPerPage=10&page=0&facets=%5B%22eventtype%22%2C%22seasonnumber%22%2C%22facilityfacet%22%2C%22genre%22%2C%22instrument%22%5D&tagFilters=&facetFilters=%5B%22eventtype%3ACarnegie%20Hall%20Presents%22%2C%22eventtype%3AFree%20Events%22%2C%22facilityfacet%3AOffsite%22%2C%5B%22facilityfacet%3AOffsite%22%5D%5D&numericFilters=%5B%22startdate%3E1572441713100%22%5D"},{"indexName":"sitecore-events","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=genre&numericFilters=%5B%22startdate%3E1572441713100%22%5D&facetFilters=%5B%22eventtype%3ACarnegie%20Hall%20Presents%22%2C%22eventtype%3AFree%20Events%22%2C%22facilityfacet%3AOffsite%22%2C%5B%22facilityfacet%3AOffsite%22%5D%5D"},{"indexName":"sitecore-events","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=facilityfacet&numericFilters=%5B%22startdate%3E1572441713100%22%5D&facetFilters=%5B%22eventtype%3ACarnegie%20Hall%20Presents%22%2C%22eventtype%3AFree%20Events%22%2C%22facilityfacet%3AOffsite%22%5D"},{"indexName":"sitecore-events","params":"query=&hitsPerPage=1&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=instrument&numericFilters=%5B%22startdate%3E1572441713100%22%5D&facetFilters=%5B%22eventtype%3ACarnegie%20Hall%20Presents%22%2C%22eventtype%3AFree%20Events%22%2C%22facilityfacet%3AOffsite%22%2C%5B%22facilityfacet%3AOffsite%22%5D%5D"}]}'

def eval():
    return requests.post('https://q0tmlopf1j-dsn.algolia.net/1/indexes/*/queries', headers=headers, params=params, data=data)

def events():
    response = eval()
    i = []
    for hit in response.json()['results'][0]['hits']:
        info = {
            'name': hit['title'],
            'date': hit['date'],
            'url': 'https://carnegiehall.org' + hit['url'],
            'time': hit['time'],
            'photos': [hit['image']['src']],
            'host': 'Carnegie Hall',
            'location_description': hit['facility'],
            'type': 'music',
            # location, description
        }

        more_info_response = requests.get(info['url'])
        soup = BeautifulSoup(more_info_response.text, 'html.parser')

        location_text = soup.find_all(class_='ch-event-facilityNotes')[0].text
        description_text = soup.find_all(class_='ch-page-hero-block__content')[0].text

        print(location_text)
        location_text = location_text.strip().split('\n')[2]
        description_text = description_text.strip()
        info['description'] = description_text

        r = search_one(location_text)
        j = r.json()['candidates'][0] # first result assumed correct
        print(location_text, j['geometry'])
        
        info['location'] = {
            'lat': j['geometry']['location']['lat'],
            'lon': j['geometry']['location']['lng']
        },
        i.append(info)
    return i


def search_one(name):
    query = name
    target = 'findplacefromtext'
    fields = {'geometry/location', 'name', 'types', 'place_id'}
    url = os.path.join(API_URL, target, OUTPUT)
    payload = {
                'locationbias': mnh_bias,
                'input': query,
                'inputtype': INPUTTYPE,
                'fields': ','.join(fields),
                'key': API_KEY
            }
    r = requests.get(url, params=payload)
    return r