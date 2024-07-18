import uuid

def convert_old_dynamo_publicart(p):
    location = {
            'name': p['name'],
            'location': {
                'lat': p['location']['lat'],
                'lon': p['location']['lng']
                },
            'createdAt': time.time(),
            'type': p['type'],
            'id': p['id'],
        }
    if 'photos' in p:
        location['photos'] = p['photos']
    return location

def update_legacy_photo(location):
    if 'photos' in location and len(location['photos']) > 0:
        # We won't bother with more than one photo for now.
        return {
            'id': str(uuid.uuid4()),
            'location_id': location['id'],
            'url': location['photos'][0],
        }