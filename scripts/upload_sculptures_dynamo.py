import boto3
import json
import decimal
import uuid

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

GOOGLE_SCULPTURE_TABLE = "GoogleSculptureTable"

def delete_table(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    print(table.delete())

def create_table(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    session = boto3.session.Session()
    client = session.client('dynamodb', region_name='us-east-1')
    client.get_waiter('table_not_exists').wait(TableName=table_name)
    print('creating table')

    table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'WriteCapacityUnits': 5,
                'ReadCapacityUnits': 5
            }
        )

    print('New table:', table_name, 'with', table.item_count, 'items.')

def add_items_to_table(table_name, items):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table(table_name)

    for sculpture in items:
        print('Adding sculpture', sculpture['name'])

        sculpture_dump = json.dumps(sculpture)
        sculpture = json.loads(sculpture_dump, parse_float=decimal.Decimal)

        response = table.put_item(Item=sculpture)
#        print(json.dumps(response, indent=4, cls=DecimalEncoder))
        print('HTTP code', response['ResponseMetadata']['HTTPStatusCode'])


