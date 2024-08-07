import requests
import os
import time

from scripts import dyn_upload
from public_art import convert_places_for_dynamo

URL = "https://maps.googleapis.com/maps/api/place/"
OUTPUT = "json"
# DO NOT SUBMIT: cannot make git repo public now.
# Maybe store elsewhere on disk
KEY = "AIzaSyCZ21RlCa8IVwxR-58b8fTgUXn_a4UYhbc"
INPUTTYPE = "textquery"
PUBLIC_ART_TABLE = "PublicArt-lnpcytykrjgmbk5nkfbmafs6dq-events"

search_query = "sculpture"
recommended_queries = ["sculpture", "mural"]

fields = {"geometry/location", "name", "types", "place_id"}
queens_bias = (
    "rectangle:40.7092498169891,-73.85618650635172|40.73060467030399,-73.81966769364828"
)
mnh_bias = "rectangle:40.72986238308025,-74.02576541648762|40.72986238308025,-74.02576541648762"

fh_origin = "40.719712,-73.838606"
jh_origin = "40.750613,-73.878024"

mnh_origins = {
    "wsp_origin": "40.727551,-73.998561",
    "battery_origin": "40.703427, -74.014586",
    "flatiron_origin": "40.742061, -73.988371",
    "rock_origin": "40.759731, -73.980847",
    "met_origin": "40.779129, -73.963025",
}

jersey_city_origin = "40.720474,-74.043823"
buff_origin = "42.912674,-78.881672"

# Fields to use in the future.
desired_fields = {"price_level", "photos"}


def validate_query(query):
    if query not in recommended_queries:
        raise ValueError("Must use a recommended query: " + str(recommended_queries))


def search_one(query=search_query):
    validate_query(query)
    target = "findplacefromtext"
    url = os.path.join(URL, target, OUTPUT)
    payload = {
        "locationbias": mnh_bias,
        "input": query,
        "inputtype": INPUTTYPE,
        "fields": ",".join(fields),
        "key": KEY,
    }
    r = requests.get(url, params=payload)
    return r


# Place api allows for up to three pages of results.
def has_next(json):
    return "next_page_token" in json


def search_nearby(origin_location=fh_origin, query=search_query):
    validate_query(query)
    target = "nearbysearch"
    url = os.path.join(URL, target, OUTPUT)
    payload = {
        "key": KEY,
        "location": origin_location,
        "rankby": "distance",
        # No need for radius when we rank by distance.
        # Returned objects will still be within some max radius
        "keyword": query,
    }
    r = requests.get(url, params=payload)
    j = r.json()
    results = j["results"]
    while has_next(j):
        time.sleep(3)
        print("Querying next page..")
        payload = {"key": KEY, "pagetoken": j["next_page_token"]}
        r = requests.get(url, params=payload)
        j = r.json()
        results = results + j["results"]

    return results


def search_and_upload(origin_location, query=search_query, table=PUBLIC_ART_TABLE):
    validate_query(query)
    items_from_google = search_nearby(origin_location, query=query)
    # Something from google w/out a photo is likely useless.
    items_from_google = [i for i in items_from_google if "photos" in i]
    print(f"Pulled {len(items_from_google)} items from google places api.")

    from_dynamo = dyn_upload.get_all_items_from_table(table)
    names = set()
    for item in from_dynamo:
        if item["type"] == query:
            names.add(item["name"])

    for item in items_from_google:
        if item["name"] not in names:
            item = convert_places_for_dynamo.convert_place_object(
                item, place_type=query
            )
            dyn_upload.add_items_to_table(
                dyn_upload.DEV_ART_TABLE, dyn_upload.DEV_PHOTOS_TABLE, [item]
            )
