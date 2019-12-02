from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from requests_aws4auth import AWS4Auth

import boto3
import hashlib
import time

PROD_HOST = 'search-publicart-o27s44277qkhxj4uh7oeph5vmq.us-east-1.es.amazonaws.com'
DEV_HOST = 'search-freedom-elasti-y6xxgzzf17nn-potbnigh4n3ug42hygqgl6g2s4.us-east-1.es.amazonaws.com'
REGION = 'us-east-1'
SERVICE = 'es'

INDEX = 'publicart'

def setup_index(client, index=INDEX):
    client.indices.create(index=index)
    body = {
        "properties": {
            "location": { "type": "geo_point"},
            "createdAt": { "type": "date" },
            "updatedAt": { "type": "date" },
        }
    }

    return client.indices.put_mapping(index=index, doc_type='doc', body=body)

def delete_index(client, index=INDEX):
    client.indices.delete(index=index)

def client(host=HOST):
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
            credentials.access_key, credentials.secret_key, REGION, SERVICE)

    es = Elasticsearch(
            hosts = [{'host': host, 'port': 443}],
            https_auth = awsauth,
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection
    )
    return es

'''
Convert from the existing google schema to our simpler schema
First change object using convert_places_for_dynamo
We want:
    location { lat, lon }
    name
    type (string: painting, sculpture, monument)
    dynamodb item id

Not needed in ES:
    date_added
    description
'''
def dyn_document_to_es_document(place):
    document = {
        'name': place['name'],
        'location': {
            # NOTE that es and google place api use different keys for longitude
            'lat': place['location']['lat'],
            'lon': place['location']['lng']
        },
        'type': 'sculpture',
        'id': place['id']
    }
    return document

# WARN: doc type used to be '_doc'
def index(client, document, index=INDEX):
    _id = hashlib.sha1(document['name'].encode()).hexdigest()
    return client.index(index=index, doc_type='doc', id=_id, body=document)

# https://elasticsearch-py.readthedocs.io/en/6.3.1/helpers.html?highlight=bulk()
def bulk_index(client, documents, index=INDEX):
    doc_type = 'doc'

    def gendata():
        for doc in documents:
            doc = dyn_document_to_es_document(doc)
            yield {
                    '_id': hashlib.sha1(doc['name'].encode()).hexdigest(),
                    '_index': index,
                    '_type': doc_type,
                    '_source': doc
            }
    return bulk(client, gendata())
