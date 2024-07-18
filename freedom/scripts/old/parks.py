import pprint
import math
import json
import re

from bs4 import BeautifulSoup

PARKS_FILE = "../parks.json"

# xml = open('nyc-parks-monuments.xml').read()
# soup = BeautifulSoup(xml, 'xml')
# rows = soup.response.row.contents


# from https://stackoverflow.com/questions/6671183
def find_center(points):
    x, y, z = 0, 0, 0

    for lat, lon in points:
        # math.cos only takes radians
        lat, lon = math.radians(float(lat)), math.radians(float(lon))
        x += math.cos(lat) * math.cos(lon)
        y += math.cos(lat) * math.sin(lon)
        z += math.sin(lat)

    x = float(x / len(points))
    y = float(y / len(points))
    z = float(z / len(points))

    return (
        math.degrees(math.atan2(z, math.sqrt(x * x + y * y))),
        math.degrees(math.atan2(y, x)),
    )


def get_data():
    with open(PARKS_FILE) as f:
        parks = json.loads(f.read())

    columns = parks["meta"]["view"]["columns"]
    rows = parks["data"]
    return {"columns": columns, "rows": rows}


def get_key_columns(keys, columns):
    ret = {}
    for i, column in enumerate(columns):
        if column["name"] in keys:
            ret[column["name"]] = i
    if len(ret) != len(keys):
        raise ValueError("A column name was not found:", ret, keys)
    return ret


def isolate_parks_and_locations():
    data = get_data()
    column_numbers = get_key_columns(["PARK_NAME", "the_geom"], data["columns"])
    name_col = column_numbers["PARK_NAME"]
    location_col = column_numbers["the_geom"]

    park_tuples = {}
    rows = data["rows"]
    for row in rows:
        name = row[name_col]
        location_pairs = re.sub("[MULTIPOLYGON()]", "", row[location_col]).strip()
        # nyc parks locations are in (long, lat) order
        location_pairs = [pair.split()[::-1] for pair in location_pairs.split(",")]

        if name and location_pairs:
            # some parks have multiple rows (split by roads)
            if name in park_tuples:
                park_tuples[name] = park_tuples[name] + location_pairs
            else:
                park_tuples[name] = location_pairs

    for park in park_tuples:
        park_tuples[park] = find_center(park_tuples[park])
    return park_tuples


def json_from_park_tuples(tuples):
    dicts = []
    for park in tuples:
        t = tuples[park]
        d = {"location": str(t[0]) + "," + str(t[1]), "name": park}
        dicts.append(d)
    return dicts


# park_tuples = []
# for row in rows:
#    name = row[name_col]
#    location_pairs = re.sub('[MULTIPOLYGON()]', '', row[location_col]).strip()
#    location_pairs = [pair.split()[::-1] for pair in location_pairs.split(',')]
#    center_location = find_center(location_pairs)
#    park_tuples.append({'name': name, 'location': center_location})
