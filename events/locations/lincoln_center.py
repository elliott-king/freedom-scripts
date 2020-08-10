import requests 

from bs4 import BeautifulSoup
from dateutil.parser import parse

from scripts import dyn_upload

url = 'http://lincolncenter.org/lincoln-center-at-home'

def events(table=dyn_upload.DEV_EVENTS_TABLE):
  events = []
  soup = BeautifulSoup(requests.get(url).text, 'html.parser')
  upcoming_shows_div = soup.find('div', id='upcoming-shows-rows-cont')
  for date_div in upcoming_shows_div.find_all('div', class_='upcoming-shows-rows'):
    date = parse(date_div['data-long'])
    for show_div in date_div.find_all('div', class_='featured-show'):
      info_div = show_div.find('div', class_='featured-show-info')
      headings_div = info_div.find('div', class_='show-info-headings')
      time = show_div.find('div', class_='featured-show-time').text.strip()
      event = {
        'name': headings_div.h1.text.strip(),
        'source': 'http://lincolncenter.org/',
        'website': headings_div.h1.a['href'],
        'host': headings_div.h3.text.strip(),
        'description': info_div.find('p', class_='show-info-description').text.strip(),
        'dates': [date.date().isoformat()],
        'times': [parse(time).time().isoformat()],
        'photos': [show_div.find('div', class_='featured-show-photo').img['src']],
        'rsvp': False,
        # TODO: quarantine only
        'location_description': 'Manhattan',
      }
      events.append(event)
  return events