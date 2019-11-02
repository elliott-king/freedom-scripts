from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from requests_aws4auth import AWS4Auth

import boto3
import hashlib
import time

HOST = 'search-freedom-elasti-tajamzilhy9i-a4vp4p7fynyjboefb2qv32fez4.us-east-1.es.amazonaws.com'
REGION = 'us-east-1'
SERVICE = 'es'

INDEX = 'event'

def setup_index(client, index=INDEX):
    client.indices.create(index=index)
    body = {
        "properties": {
            "location": { "type": "geo_point"},
            "datetime": { "type": "date" }
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
