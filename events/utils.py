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