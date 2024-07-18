import requests

from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.parser import parse

from scripts import dyn_upload

base = "http://www.flushingtownhall.org"
page = "/free-program"

api_base = "https://apps.vendini.com"
api_page = "/ticketLine/events/list"
payload = {
    "format": "json",
    "includePrices": 1,
    "page": 1,
    "w": "71988145d2eb1fdae0737b86ce843358",
}


def events(table=dyn_upload.DEV_EVENTS_TABLE):
    r = requests.get(api_base + api_page, params=payload).json()
    events = []
    venues = {}
    for venue in r["venues"]:
        venues[venue["venueID"]] = venue["name"]
    for entry in r["events"]:
        if entry["cancelled"]:
            continue
        event = {
            "name": entry["title"],
            "description": entry["description"],
            "website": base + "/event/" + entry["eventID"],
            "host": "Flushing Town Hall",
            "rsvp": False,
            "source": base,
        }
        if "cancel" in event["name"].lower():
            continue
        if "showbillPath" in entry:
            event["photos"] = [api_base + entry["showbillPath"]]

        if "flushing town hall" in venues[entry["venueID"]].lower():
            event["location_description"] = "137-35 Northern Boulevard, Flushing, NY"
        else:
            event["location_description"] = venues[entry["venueID"]]
        # TODO: could also look for '.. at ..' in event title
        if "queens center mall" in event["name"].lower():
            event["location_description"] = "Queens Center Mall"

        if entry["ticketTypesAvailable"]:
            event["rsvp"] = True

        event_soup = BeautifulSoup(requests.get(event["website"]).text, "html.parser")
        subheader = event_soup.find("span", itemprop="description").strong.text.split(
            "|"
        )
        subheader = "".join(subheader[:3])
        if "-" in subheader:
            am = False
            if "am" in subheader.lower():
                am = True
            subheader = subheader.split("-")[0]
            if am:
                subheader += "AM"
            else:
                subheader += "PM"
        dt = parse(subheader)
        event["dates"] = [str(dt.date())]
        event["times"] = [str(dt.time())]

        if not dyn_upload.is_uploaded(event, table=table):
            events.append(event)
    return events
