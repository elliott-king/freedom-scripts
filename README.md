# freedom-scripts

Our initial data is being taken from Google Places API search.

We are then interested in modifying it, and uploading it to DynamoDB & ElasticSearch. DynamoDB is intended to be our 'source of truth:' it will contain everything about these items. ES will only be needed for the location search by lat, long.

