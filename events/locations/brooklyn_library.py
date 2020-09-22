import requests 
from bs4 import BeautifulSoup
from dateutil.parser import parse

from scripts import dyn_upload
from events import utils
from events import types

url = 'https://www.bklynlibrary.org'
page = '/calendar/list'
query = '?page='

def events(table=dyn_upload.DEV_EVENTS_TABLE):
  events = []
  for i in range(0, 5):
    print('Now on page:', i)
    listpage = BeautifulSoup(requests.get(url + page + query + str(i)).text, 'html.parser')
    eventdivs = listpage.find_all('div', class_='EVENT')
    for ediv in eventdivs:
      event = {
          'source': url,
          'host': 'Brooklyn Public Library', # TODO: fix when quarantine ends
          'location_description': 'Brooklyn', # TODO: same
          'dates': [],
          'times': [],
          'photos': [],
      }
      meta = ediv.find('p', class_='meta') # date, time, location

      title = ediv.find('h4')
      event['name'] = title.text.strip()
      event['website'] = url + title.find('a')['href']
      event['photos'].append(url + ediv.find('img')['src'])

      if 'virtual' not in meta.text.lower():
        # print('Has a location not of the interweb!')
        # print(event['name'], event['website'])
        continue

      eventpage = BeautifulSoup(requests.get(event['website']).text, 'html.parser')

      date_span = eventpage.find('span', class_='icon-calendar')
      date = parse(date_span['content'])
      event['dates'].append(date.date().isoformat())
      event['times'].append(date.time().isoformat())

      description_div = eventpage.find('div', class_='pane-node-body')
      event['description'] = description_div.text.strip()

      def extract_text(node):
        return node.text.strip()
      description_divs = eventpage.find_all('div', class_='pane-entity-field')
      long_description = ' '.join(list(map(extract_text, description_divs)))
      event['rsvp'] = types.rsvp(long_description)

      events.append(event)
  return events