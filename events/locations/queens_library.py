import json
import requests 
from bs4 import BeautifulSoup
from dateutil.parser import parse

from scripts import dyn_upload


URL = 'https://www.queenslibrary.org'
# first page has no value but has different directory
# next page is 1, value of zero will return no html
FIRST_PAGE = '/calendar?searchField=*&category=calendar&fromlink=calendar&searchFilter='
FUTURE_PAGES = '/search/call?searchField=*&category=calendar&searchFilter=&pageParam='

def events(table=dyn_upload.DEV_EVENTS_TABLE):

  events = []
  for i in range(0, 8):
    print('Now on page:', i)
    eventdivs = get_eventdivs(i)
    for ediv in eventdivs:
      events.append(event_from_div(ediv))
  return events

def get_eventdivs(page_number):
  target_url = URL
  if page_number:
    target_url += FUTURE_PAGES + str(page_number)
  else:
    target_url += FIRST_PAGE

  listpage = BeautifulSoup(requests.get(target_url).text, 'html.parser')
  return listpage.find_all('div', class_='search-results card')

def event_from_div(div):
    event = {
        'source': URL,
        'host': 'Queens Public Library', # TODO: fix when quarantine ends
        'location_description': 'Queens', # TODO: same
        'rsvp': False, # TODO: fix when quarantine ends
    }

    if div.img:
      event['photos'] = [div.find('img')['src']]

    values_from_script = parse_script(div)
    event = {**event, **values_from_script}

    desc_dict = parse_eventpage(event['website'])
    event = {**event, **desc_dict}

    return event

# Script attached to each div. Much of this info is not initially in the HTML, 
# is added after by way of the script.
def parse_script(div):
    script = div.script.get_text()
    # simplified parsing of their simple script
    # remove unnecessary single quote and semicolon
    json_dict = script.split(' = ')[1][1:-2] 

    event_dict = json.loads(json_dict.replace('&quot;', '"'))
    date = parse(event_dict['date_event'].split(' - ')[0])

    return {
      'name': event_dict['title'],
      'website': URL + event_dict['callUrl'],
      'dates': [date.date().isoformat()],
      'times': [date.time().isoformat()]
    }

def parse_eventpage(url):
  page = BeautifulSoup(requests.get(url).text, 'html.parser')
  ediv = page.find('div', class_='event-node-details')
  desc_div = ediv.find('div', class_='description')
  return {
    'description': desc_div.get_text()
  }