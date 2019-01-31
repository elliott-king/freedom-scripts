import boto3
import json
import decimal
import uuid

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

HELLO_WORLD_ID = "08a8f7f0-6789-4c0e-af8b-6d6b04488046"

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


# region list: https://docs.aws.amazon.com/general/latest/gr/rande.html
# endpoint a4b.us-east-1.amazonaws.com

def deleteTable(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    print(table.delete())

def createTable(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    session = boto3.session.Session()
    client = session.client('dynamodb', region_name='us-east-1')
    client.get_waiter('table_not_exists').wait(TableName=table_name)
    print('creating table')

    table = dynamodb.create_table(
            TableName='FreedomLocationTable',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'WriteCapacityUnits': 5,
                'ReadCapacityUnits': 5
            }
        )
    print(table.item_count)

def deleteAndRecreateTable(table_name):
    deleteTable(table_name)
    createTable(table_name)

def addItemsToTable(items):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('FreedomLocationTable')

    for park in items:
        (latitude, longitude) = items[park]
        item_type = 'monument'
        item_id = uuid.uuid4()
        i = {
                'id': str(item_id),
                'name': park,
                'latitude': decimal.Decimal(str(latitude)),
                'longitude': decimal.Decimal(str(longitude)),
                'type': item_type
            }

        print('adding monument:', i)

        response = table.put_item(Item=i)
        print(json.dumps(response, indent=4, cls=DecimalEncoder))


