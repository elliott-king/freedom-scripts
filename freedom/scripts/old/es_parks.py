from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from requests_aws4auth import AWS4Auth

import boto3  # Amazon Python SDK
import hashlib

# set location field as geo_point
# from https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-geohashgrid-aggregation.html
# curl -XPUT
# "https://search-freedom-locations-test-zj3i4hp466x4rddyw6wwgaaovm.us-east-1.es.amazonaws.com/parks" -H 'Content-Type: application/json' -d '{"mappings": { "_doc": { "properties": { "location": { "type": "geo_point"} } } } }'

# delete index
# curl -XDELETE "https://search-freedom-locations-test-zj3i4hp466x4rddyw6wwgaaovm.us-east-1.es.amazonaws.com/parks"

# IMPORTANT: must not have 'http://' or ending slash!
HOST = "search-freedom-locations-test-zj3i4hp466x4rddyw6wwgaaovm.us-east-1.es.amazonaws.com"
REGION = "us-east-1"
SERVICE = "es"


def client():
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, REGION, SERVICE)

    es = Elasticsearch(
        hosts=[{"host": HOST, "port": 443}],
        https_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
    return es


def index(client, document):
    _id = hashlib.sha1(document["name"].encode()).hexdigest()
    return client.index(index="parks", doc_type="_doc", id=_id, body=document)


def bulk_index(client, documents):
    index = "parks"
    doc_type = "_doc"

    def gendata():
        for doc in documents:
            yield {
                "_id": hashlib.sha1(doc["name"].encode()).hexdigest(),
                "_index": index,
                "_type": doc_type,
                "_source": doc,
            }

    # bulk helpers:
    # https://elasticsearch-py.readthedocs.io/en/6.3.1/helpers.html?highlight=bulk()
    return bulk(client, gendata())
