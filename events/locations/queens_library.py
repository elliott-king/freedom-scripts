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


# look for 'search-results' & 'card'
# '{&quot;jobID&quot;:&quot;000490-0820&quot;,&quot;title&quot;:&quot;Staying Safe While Staying Home&quot;,&quot;descr&quot;:&quot;Learn About:&lt;br&gt;1) Increased risks for unintentional poisonings while staying at home during COVID-19&lt;br&gt;-Cleaning ...&quot;,&quot;callUrl&quot;:&quot;\/calendar\/staying-safe-while-staying-home\/000490-0820&quot;,&quot;PDF&quot;:&quot;000490-08-20_000490.pdf&quot;,&quot;prgm_image&quot;:&quot;000490-08-20_147.jpg&quot;,&quot;prgm_age&quot;:&quot;Adults&quot;,&quot;prgm_type&quot;:&quot;Health Workshops&quot;,&quot;rgstrtion&quot;:false,&quot;staff_only&quot;:0,&quot;wait_list&quot;:null,&quot;single_shared&quot;:0,&quot;action&quot;:&quot;updateJobWeb&quot;,&quot;updated&quot;:&quot;&quot;,&quot;updated_timestamp&quot;:&quot;&quot;,&quot;branch_name&quot;:&quot;Virtual&quot;,&quot;date_show&quot;:&quot;Sep 21, 6:00pm - 8:00pm&quot;,&quot;date_show_timestamp&quot;:1600725600,&quot;branch_location&quot;:&quot;99970000&quot;,&quot;all_times&quot;:{&quot;1600725600&quot;:&quot;Sep 21, 6:00pm - 8:00pm&quot;},&quot;set_of_timestamp&quot;:[1600725600],&quot;descrQV&quot;:&quot;Learn About:&lt;br&gt;1) Increased risks for unintentional poisonings while staying at home during COVID-19&lt;br&gt;-Cleaning ...&quot;,&quot;prgmAge&quot;:&quot;For Adults&quot;,&quot;cal_image_small&quot;:&quot;https:\/\/image.queenslibrary.org\/lamps\/styles\/event_small\/000490-08-20_147.jpg&quot;,&quot;cal_image_large&quot;:&quot;https:\/\/image.queenslibrary.org\/lamps\/styles\/event_large\/000490-08-20_147.jpg&quot;,&quot;date_event&quot;:&quot;Sep 21, 6:00pm - 8:00pm&quot;,&quot;widgetParam2&quot;:3}'
# arrJsonData_cal['000266-0720'] = '{&quot;jobID&quot;:&quot;000266-0720&quot;,&quot;title&quot;:&quot;Coffee Chat with the Curator of the Black Heritage Reference Center&quot;,&quot;descr&quot;:&quot;Join the Curator Tuesdays at 4pm. &lt;br&gt;9\/22 -Virtual Views: Gordon Parks MoMA takes a close look at this influential...&quot;,&quot;callUrl&quot;:&quot;\/calendar\/coffee-chat-with-the-curator-of-the-black-heritage-reference-center\/000266-0720&quot;,&quot;PDF&quot;:&quot;000266-07-20_000266.pdf&quot;,&quot;prgm_image&quot;:&quot;000266-07-20_266.jpg&quot;,&quot;prgm_age&quot;:&quot;Adults&quot;,&quot;prgm_type&quot;:&quot;Black Heritage&quot;,&quot;rgstrtion&quot;:false,&quot;staff_only&quot;:0,&quot;wait_list&quot;:null,&quot;single_shared&quot;:0,&quot;action&quot;:&quot;updateJobWeb&quot;,&quot;updated&quot;:&quot;&quot;,&quot;updated_timestamp&quot;:&quot;&quot;,&quot;branch_name&quot;:&quot;Virtual&quot;,&quot;date_show&quot;:&quot;Sep 22, 4:00pm - 5:00pm&quot;,&quot;date_show_timestamp&quot;:1600804800,&quot;branch_location&quot;:&quot;99970000&quot;,&quot;all_times&quot;:{&quot;1600804800&quot;:&quot;Sep 22, 4:00pm - 5:00pm&quot;,&quot;1601409600&quot;:&quot;Sep 29, 4:00pm - 5:00pm&quot;},&quot;set_of_timestamp&quot;:[1600804800,1601409600],&quot;descrQV&quot;:&quot;Join the Curator Tuesdays at 4pm. &lt;br&gt;9\/22 -Virtual Views: Gordon Parks MoMA takes a close look at this influential...&quot;,&quot;prgmAge&quot;:&quot;For Adults&quot;,&quot;cal_image_small&quot;:&quot;https:\/\/image.queenslibrary.org\/lamps\/styles\/event_small\/000266-07-20_266.jpg&quot;,&quot;cal_image_large&quot;:&quot;https:\/\/image.queenslibrary.org\/lamps\/styles\/event_large\/000266-07-20_266.jpg&quot;,&quot;date_event&quot;:&quot;Sep 22, 4:00pm - 5:00pm&quot;,&quot;widgetParam2&quot;:3}';
# arrJsonData_cal['000463-0820'] = '{&quot;jobID&quot;:&quot;000463-0820&quot;,&quot;title&quot;:&quot;Puppet Making Workshop&quot;,&quot;descr&quot;:&quot;Join Nicola the puppeteer for a 40-minute virtual puppet craft-making workshop! Get ready to use whatever materials...&quot;,&quot;callUrl&quot;:&quot;\/calendar\/puppet-making-workshop\/000463-0820&quot;,&quot;PDF&quot;:&quot;000463-08-20_000463.pdf&quot;,&quot;prgm_image&quot;:&quot;000463-08-20_Children Puppet.jpg&quot;,&quot;prgm_age&quot;:&quot;Kids&quot;,&quot;prgm_type&quot;:&quot;Children\u2019s Program, General&quot;,&quot;rgstrtion&quot;:false,&quot;staff_only&quot;:0,&quot;wait_list&quot;:null,&quot;single_shared&quot;:0,&quot;action&quot;:&quot;updateJobWeb&quot;,&quot;updated&quot;:&quot;&quot;,&quot;updated_timestamp&quot;:&quot;&quot;,&quot;branch_name&quot;:&quot;Virtual&quot;,&quot;date_show&quot;:&quot;Sep 30, 4:00pm - 4:45pm&quot;,&quot;date_show_timestamp&quot;:1601496000,&quot;branch_location&quot;:&quot;99970000&quot;,&quot;all_times&quot;:{&quot;1601496000&quot;:&quot;Sep 30, 4:00pm - 4:45pm&quot;,&quot;1603310400&quot;:&quot;Oct 21, 4:00pm - 4:45pm&quot;},&quot;set_of_timestamp&quot;:[1601496000,1603310400],&quot;descrQV&quot;:&quot;Join Nicola the puppeteer for a 40-minute virtual puppet craft-making workshop! Get ready to use whatever materials...&quot;,&quot;prgmAge&quot;:&quot;For Kids&quot;,&quot;cal_image_small&quot;:&quot;https:\/\/image.queenslibrary.org\/lamps\/styles\/event_small\/000463-08-20_Children Puppet.jpg&quot;,&quot;cal_image_large&quot;:&quot;https:\/\/image.queenslibrary.org\/lamps\/styles\/event_large\/000463-08-20_Children Puppet.jpg&quot;,&quot;date_event&quot;:&quot;Sep 30, 4:00pm - 4:45pm&quot;,&quot;widgetParam2&quot;:3}';

def events(table=dyn_upload.DEV_EVENTS_TABLE):

  events = []
  for i in range(0, 8):
    print('Now on page:', i)
    eventdivs = get_eventdivs(i)
    for ediv in eventdivs:
      events.append(event_from_div(ediv))
  print('Number events:', len(events))
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