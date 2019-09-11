import requests
import boto3
import uuid
import shutil
import time

import magic

name_to_extension = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        }

client = boto3.client('s3')
bucket = 'freedom-js-appb7dc6789c3d248c18c4e34a5eb639543-freedom'

def get_photo(url):
    name = uuid.uuid4()
    r = requests.get(url, stream=True)
    with open('photos/' + str(name), 'wb') as out_file:
        shutil.copyfileobj(r.raw, out_file)
    del r
    extension = magic.from_file('photos/' + str(name), mime=True)
    print(extension)

    filename = str(name) + name_to_extension[extension]
    response = client.upload_file(
            'photos/'+str(name), 
            bucket, 
            'public/{}'.format(filename),
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': extension
            }
        )
    time.sleep(3)
    photo_url = 'https://' + bucket + '.s3.amazonaws.com' + '/public/' + filename
    return photo_url
