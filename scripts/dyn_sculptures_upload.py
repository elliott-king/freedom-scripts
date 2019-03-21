import boto3
import json
import decimal
import uuid

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# Stores items exactly as they are structured from the Google Places API
GOOGLE_SCULPTURE_TABLE = "GoogleSculptureTable"

# Restructured table using convert_places_for_dynamo.py
OUR_TABLE = "FreedomLocationAlphaTable"

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def delete_table(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    print(table.delete())

def create_table(table_name, key_column='name'):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    session = boto3.session.Session()
    client = session.client('dynamodb', region_name='us-east-1')
    client.get_waiter('table_not_exists').wait(TableName=table_name)
    print('creating table')

    table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': key_column,
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': key_column,
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

        sculpture = json.dumps(sculpture, cls=DecimalEncoder)
        # DynamoDB does not take float values.
        sculpture = json.loads(sculpture, parse_float=decimal.Decimal)

        response = table.put_item(Item=sculpture)
        print('HTTP code', response['ResponseMetadata']['HTTPStatusCode'])


def get_all_items_from_table(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    
    response = table.scan()
    return response['Items']
