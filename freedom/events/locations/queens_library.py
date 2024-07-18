import json
import requests

from bs4 import BeautifulSoup, ResultSet, PageElement
from dateutil.parser import parse

from freedom.events.models import Event


URL = "https://www.queenslibrary.org"
# first page has no value but has different directory
# next page is 1, value of zero will return no html
FIRST_PAGE = "/calendar?searchField=*&category=calendar&fromlink=calendar&searchFilter="
FUTURE_PAGES = "/search/call?searchField=*&category=calendar&searchFilter=&pageParam="
END_RANGE = 0  # fixme: Can use up to 8


def events():

    ql_events: list[Event] = []
    for i in range(0, 1):
        print("Now on page:", i)
        eventdivs = get_eventdivs(i)
        for ediv in eventdivs:
            try:
                event = event_from_div(ediv)
            except Exception as e:
                print("IGNORING qpl event with parsing error: ", e)
                continue

            if not event.location_description:
                print(f"IGNORING qpl {event.name}:{event.website}: a virtual event")
                continue

            # print('event:') # useful for debugging
            ql_events.append(event)
    return ql_events


def get_eventdivs(page_number) -> ResultSet[PageElement]:
    target_url = URL
    if page_number:
        target_url += FUTURE_PAGES + str(page_number)
    else:
        target_url += FIRST_PAGE

    listpage = BeautifulSoup(requests.get(target_url).text, "html.parser")
    return listpage.find_all("div", class_="search-results card")


def event_from_div(div: PageElement):
    event = Event(source=URL, host="Queens Public Library")
    # event = {
    #     'source': URL,
    #     'host': 'Queens Public Library', # TODO: fix when quarantine ends
    #     'location_description': None, # TODO: same
    #     'rsvp': False, # TODO: fix when quarantine ends
    # }

    if div.img:
        event.photos = [div.find("img")["src"]]

    parse_script(div, event)
    parse_eventpage(event.website, event)
    return event


# Script attached to each div. Much of this info is not initially in the HTML,
# is added after by way of the script.
def parse_script(div: PageElement, event: Event):
    script = div.script.get_text()
    # simplified parsing of their simple script
    # remove unnecessary single quote and semicolon
    json_dict = script.split(" = ")[1][1:-2]

    try:
        json_dict = json_dict.replace("&quot;", '"')
        event_dict = json.loads(json_dict)
    except Exception as e:
        print("issue parsing qpl event json dict", json_dict)
        raise e

    try:
        date = parse(event_dict["date_event"].split(" - ")[0])
    except Exception as e:
        print(
            f"issue parsing qpl date on {event_dict['title']}: "
            f"'{event_dict['date_event']}' {URL + event_dict['callUrl']}"
        )
        raise e

    # d = {
    #   'name': event_dict['title'],
    #   'website': URL + event_dict['callUrl'],
    #   'dates': [date.date().isoformat()],
    #   'times': [date.time().isoformat()],
    # }
    event.name = event_dict["title"]
    event.website = URL + event_dict["callUrl"]
    event.datetimes = [date]

    branch = event_dict.get("branch_name", None)
    if branch:
        if branch.lower() == "Poppenhusen":
            event.location_description = branch
        else:
            event.location_description = branch + " Library"


def parse_eventpage(url: str, event: Event):
    page = BeautifulSoup(requests.get(url).text, "html.parser")
    ediv = page.find("div", class_="event-node-details")
    desc_div = ediv.find("div", class_="description")
    event.description = desc_div.get_text().strip()

    address_div = ediv.find("div", class_="address")
    address = None
    if address_div:
        address = address_div.get_text().strip()
        event.location_description = address
