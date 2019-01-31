'''
Using elasticsearch geo queries.
https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-queries.html
'''

from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from requests_aws4auth import AWS4Auth

import boto3
import requests

# TODO: consider using geo_shape for polygons instead of just geo_point?
# May be irrelevant for monuments, small things, etc.
# https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-shape.html

# TODO: needs to handle aws auth. Currently, the es is setup to allow all
# queries from this ip.

HOST = 'https://search-freedom-locations-test-zj3i4hp466x4rddyw6wwgaaovm.us-east-1.es.amazonaws.com/'
INDEX = 'parks'
REGION = 'us-east-1'
DOC_TYPE = '_doc'
SERVICE = 'es'

def client():
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
            credentials.access_key, credentials.secret_key, REGION, SERVICE)

    es = Elasticsearch(
            hosts = [{'host': HOST, 'port': 443}],
            https_auth = awsauth, 
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection
    )
    return es

def create_auth():
    credentials = boto3.Session().get_credentials()
    return AWS4Auth(credentials.access_key, credentials.secret_key, REGION, SERVICE)

def search_query(json):
    url = HOST + INDEX + '/_search'
    return requests.get(url, auth=create_auth(), json=json)

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
        limit=10):

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
    return search_query(payload)

