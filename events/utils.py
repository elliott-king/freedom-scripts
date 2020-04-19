EVENT_TYPES = [
    "advocacy",
    "art",
    "athletics",
    "comedy",
    "crafts",
    "dance",
    "diy",
    "education",
    "fashion",
    "family",
    "film",
    "food",
    "games",
    "health_medical",
    "history",
    "holiday",
    "library",
    "literature",
    "lgbtq",
    "music",
    "nature",
    "new_york",
    "philosophy",
    "science",
    "senior",
    "shopping",
    "spirituality",
    "teen",
    "theater",
    "technology",
    "world_events",
]

def add_type(event, typename, strings, extra_search=[]):
    type_in_event = False
    for s in strings:
        if s in event['name'].lower() or ('description' in event and s in event['description'].lower()):
            type_in_event = True
    if type_in_event and 'types' in event and typename not in event['types']:
        event['types'].append(typename)

def in_prev_parsed_events(prev_events, event, onetime_date=None):
    name = event['name'].lower().strip()
    if name in prev_events:
        prev = prev_events[name]
        if 'host' in event:
            d = set()
            if onetime_date:
                d.add(onetime_date)
            if 'dates' in event:
                d = set(event['dates'])
            for p in prev:
                if not d.isdisjoint(p['dates']) and event['host'] == p['host']:
                    print('Already parsed', event['name'], 'for host', event['host'])
                    return True
    return False

def add_to_prev_events(prev_events, event):
    name = event['name'].lower().strip()
    prev_events[name].append({'dates': set(event['dates']), 'host': event['host']})