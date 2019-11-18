from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from requests_aws4auth import AWS4Auth

import boto3
import hashlib
import time
import requests

PROD_HOST = 'search-freedom-elasti-tajamzilhy9i-a4vp4p7fynyjboefb2qv32fez4.us-east-1.es.amazonaws.com'
DEV_HOST = 'search-freedom-elasti-bt4tf0jcyqii-kb65ab75r6ydviujronn6g7yui.us-east-1.es.amazonaws.com'
REGION = 'us-east-1'
SERVICE = 'es'

INDEX = 'event'

def setup_index(client, index=INDEX):
    client.indices.create(index=index)
    body = {
        "properties": {
            "location": { "type": "geo_point"},
            "dates": { "type": "date"},
            "times": { "type": "text"}
        }
    }

    return client.indices.put_mapping(index=index, doc_type='doc', body=body)

def delete_index(client, index=INDEX):
    client.indices.delete(index=index)

def client(host):
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

def snapshot_creds():
    credentials = boto3.Session().get_credentials()
    return AWS4Auth(
        credentials.access_key,
        credentials.secret_key, 
        REGION, SERVICE, 
        session_token=credentials.token)

# May need to re-register: S3 buckets in us-east-1 need a different label?
# https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-managedomains-snapshots.html#es-managedomains-snapshot-registerdirectory
def register_snapshot_repo(host):
    awsauth = snapshot_creds()
    host = 'https://' + host + '/'
    path = '_snapshot/my-snapshot-repo'
    url = host + path

    payload = {
        'type': 's3',
        'settings': {
            'bucket': 'es-freedom-snapshot',
            'region': REGION,
            'role_arn': 'arn:aws:iam::888096637450:role/es_snapshot_role'
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }

    return requests.put(url, auth=awsauth, json=payload, headers=headers)

def take_snapshot(host, name):
    awsauth = snapshot_creds()
    host = 'https://' + host + '/'
    path = '_snapshot/my-snapshot-repo/' + name
    url = host + path
    return requests.put(url, auth=awsauth)

# Can also restore a specific index, see code:
# https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-managedomains-snapshots.html#es-managedomains-snapshot-client-python
def restore_snapshot(host, name):
    awsauth = snapshot_creds()
    host = 'https://' + host + '/'
    path = '_snapshot/my-snapshot-repo/' + name + '/_restore'
    url = host + path
    return requests.post(url, auth=awsauth)

def view_snapshots(host):
    awsauth = snapshot_creds()
    host = 'https://' + host + '/'
    path = '_snapshot/my-snapshot-repo/_all?pretty'
    url = host + path
    return requests.get(url, auth=awsauth)
