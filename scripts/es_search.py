'''
Using elasticsearch geo queries.
https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-queries.html
'''

from requests_aws4auth import AWS4Auth

import boto3
import requests
import hashlib

# TODO: consider using geo_shape for polygons instead of just geo_point?
# May be irrelevant for monuments, small things, etc.
# https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-shape.html

HOST = 'https://search-freedom-locations-test-zj3i4hp466x4rddyw6wwgaaovm.us-east-1.es.amazonaws.com/'
INDEX = 'parks'
REGION = 'us-east-1'
SERVICE = 'es'

HOST_SCULPTURES = 'https://search-publicart-o27s44277qkhxj4uh7oeph5vmq.us-east-1.es.amazonaws.com/'
INDEX_SCULPTURES = 'public_art'

def create_auth():
    credentials = boto3.Session().get_credentials()
    return AWS4Auth(credentials.access_key, credentials.secret_key, REGION, SERVICE)

def search_query(json, host=HOST, index=INDEX):
    url = host + index + '/_search'
    return requests.get(url, auth=create_auth(), json=json)

def find_one_park(park_name, host=HOST, index=INDEX):
    url = host + index + '/doc' + '/_search'
#    _id = hashlib.sha1(document['name'].encode()).hexdigest()
    payload = {
            "query": { "match_exactly": { "name": park_name } }
    }
#    payload = {'q': park_name}
    return requests.get(url, auth=create_auth())

# Expected distance in km
def find_close_objects(lat, lon, dist=1, limit=10):
    payload = {
        "from": 0, "size": limit,
        "query": {
            "bool" : {
                "must" : {
                    "match_all" : {}
                },
                "filter" : {
                    "geo_distance" : {
                        "distance" : str(dist) + "km",
                        "location" : {
                            "lat" : lat,
                            "lon" : lon
                        }
                    }
                }
            }
        }
    }
    return search_query(payload)

def find_in_bounding_box(
        top_left_lat, top_left_lon, 
        bot_right_lat, bot_right_lon,
        limit=10,
        host=HOST,
        index=INDEX):

    payload = {
        "from": 0, "size": limit,
        "query": {
            "bool" : {
                "must" : {
                    "match_all" : {}
                },
                "filter" : {
                    "geo_bounding_box" : {
                        "location" : {
                            "top_left" : {
                                "lat" : top_left_lat,
                                "lon" : top_left_lon
                            },
                            "bottom_right" : {
                                "lat" : bot_right_lat,
                                "lon" : bot_right_lon
                            }
                        }
                    }
                }
            }
        }
    }
    return search_query(payload, host=host, index=index)

