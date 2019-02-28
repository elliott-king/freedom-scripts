from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from requests_aws4auth import AWS4Auth

import boto3
import hashlib
import time

HOST = 'search-publicart-o27s44277qkhxj4uh7oeph5vmq.us-east-1.es.amazonaws.com'
REGION = 'us-east-1'
SERVICE = 'es'

INDEX = 'public_art'

def setup_index(client):
    client.indices.create(index=INDEX)
    body = {
        "properties": {
            "location": { "type": "geo_point"},
            "date_added": { "type": "date" }
        }
    }

    return client.indices.put_mapping(index=INDEX, doc_type='_doc', body=body)

def delete_index(client):
    client.indices.delete(index=INDEX)

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

'''
Convert from the existing google schema to our simpler schema
We want:
    location { lat, lon }
    name
    description
    date_added
    type (string: painting, sculpture, monument)

Eventually:
    photo
'''
def translate_google_response_to_document(place):
    document = {
        'name': place['name'],
        'location': {
            # NOTE that es and google place api use different keys for longitude
            'lat': place['geometry']['location']['lat'],
            'lon': place['geometry']['location']['lng']
        },
        'date_added': time.time(),
        'type': 'sculpture'
    }
    return document

def index(client, document):
    _id = hashlib.sha1(document['name'].encode()).hexdigest()
    return client.index(index=INDEX, doc_type='_doc', id=_id, body=document)

# https://elasticsearch-py.readthedocs.io/en/6.3.1/helpers.html?highlight=bulk()
def bulk_index(client, documents):
    index = INDEX
    doc_type = '_doc'

    def gendata():
        for doc in documents:
            doc = translate_google_response_to_document(doc)
            yield {
                    '_id': hashlib.sha1(doc['name'].encode()).hexdigest(),
                    '_index': index,
                    '_type': doc_type,
                    '_source': doc
            }
    return bulk(client, gendata())
