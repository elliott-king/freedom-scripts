import requests

from dateutil.parser import parse
import json

from scripts import dyn_upload
from events import utils
from events import types

# There are a few events endpoints. event-programs includes locations, the others don't
# For reference, visit https://refinery.nypl.org/api/nypl with NO EXTRA SLASHES
url = "https://refinery.nypl.org/api/nypl/"
api_endpoint = "ndo/v0.1/content/nodes/event-programs"
page = "?page[number]="

nypl_url = "https://www.nypl.org"


def events(table=dyn_upload.DEV_EVENTS_TABLE):
    events = []
    for page_suffix in [str(x) for x in range(1, 13)]:
        # todo: rate limit this?
        print("now looking at page", page_suffix)
        page_json = json.loads(
            requests.get(url + api_endpoint + page + page_suffix).text
        )
        events_json = page_json["data"]
        events += parse_multi_events_json(events_json)
    return events


def parse_multi_events_json(multi_events_json):
    events = []
    for event_json in multi_events_json:
        event = parse_single_event_json(event_json)
        if event:
            events.append(event)
    return events


def parse_single_event_json(event_json):
    if event_json["attributes"]["event-status"]:
        return False

    start_date = parse(event_json["attributes"]["start-date"])
    end_date = parse(event_json["attributes"]["end-date"])

    event = {
        "source": nypl_url,
        "dates": [start_date.date().isoformat()],
        "times": [start_date.time().isoformat(), end_date.time().isoformat()],
        "name": event_json["attributes"]["name"]["en"]["text"],
        "website": event_json["attributes"]["uri"]["full-uri"],
        "description": event_json["attributes"]["description"]["en"]["short-text"],
    }

    library_url = event_json["relationships"]["location"]["links"]["self"]
    library_json = json.loads(requests.get(library_url).text)
    library = parse_library_json(library_json)
    event["host"] = library["host"]
    event["location_description"] = library["location_description"]

    full_description = event_json["attributes"]["description"]["en"]["full-text"]

    event["rsvp"] = not not event_json["attributes"][
        "registration-type"
    ] or types.infer_rsvp(full_description)

    return event


def parse_library_json(library_json):
    return {
        "host": library_json["data"]["attributes"]["full-name"],
        "location_description": library_json["data"]["attributes"]["address"][
            "address1"
        ]
        + ", "
        + library_json["data"]["attributes"]["address"]["city"],
    }
