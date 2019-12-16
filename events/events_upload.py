import boto3
import json
import decimal
import uuid

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# Updating items after a full table scan.
# table.update_item(Key={'id': item['id']}, UpdateExpression='set permanent = :r', ExpressionAttributeValues={':r': 'true'})

EVENTS_TABLE = 'Event-cevvqsg2rzeifnuzezmiqvz3bu-freedom'
DEV_EVENTS_TABLE = 'Event-lnpcytykrjgmbk5nkfbmafs6dq-events'

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def add_items_to_table(table_name, items):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table(table_name)

    previous = set(i['name'].lower() for i in table.scan(AttributesToGet=['name'])['Items'])
    print(previous)

    for i in items:
        i['id'] = str(uuid.uuid4())
        if i['name'].lower() in previous:
            print('Cannot add: "', i['name'], '" already exists in dynamodb.')
        else:
            print('Adding event', i['name'])

            i = json.dumps(i, cls=DecimalEncoder)
            # DynamoDB does not take float values.
            i = json.loads(i, parse_float=decimal.Decimal)

            response = table.put_item(Item=i)
            print('HTTP code', response['ResponseMetadata']['HTTPStatusCode'])
        
def get_all_items_from_table(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    
    response = table.scan()
    return response['Items']

