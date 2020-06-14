Web scrapers for free events in NYC. 

Intended as support for my [free events webapp](https://github.com/elliott-king/freedom-js-app). To run, you will need a new Google Maps API key (this one is restricted for my machine only).

**Disclaimer**: it's pretty all over the place. Many of these may not work very well.

## Events
Each scraper is written to the needs of the site. **If you know of an API for NYPL events**, please let me know.

## public art

Our initial data is being taken from Google Places API search.

We are then interested in modifying it, and uploading it to DynamoDB & ElasticSearch. DynamoDB is intended to be our source of truth: it will contain everything about these items. ES will only be needed for the location search by lat, long.