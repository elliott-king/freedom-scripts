import re
import os
import datetime

from dateutil.parser import parse

TEXT = 'nonsense_11-8_11-14.txt'
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nonsense', TEXT)

weekdays = ['MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY']

def contents():
    with open(PATH, 'r') as f:
        return f.read()


def events(s=contents()):
    header = r'[X\*]{5}(.*?)[X\*]{5}'
    events = []
    start = 0

    # First, we simply split the text by headers
    h_iter = re.finditer(header, s)
    for match in h_iter:
        text = s[start:match.start()].strip()
        start = match.start()
        if '$free' in text:
            splits = text.split('\n')
            e = {
                'name': splits[3],
                'source': 'http://www.nonsensenyc.com/',
                'website': splits[-1],
                'location_description': splits[-3],
                'description': '\n'.join(splits[5:]),
                'rsvp': 'rsvp' in text.lower() or 'registration' in text.lower()
            }
            if splits[-4].strip():
                e['host'] = splits[-4]
            
            # Handling dates
            h = re.match(header, text).group(1).strip()
            try:    
                e['dates'] = str(parse(h).date())
            except ValueError:
                today = datetime.date.today()
                for w in weekdays:
                    if w in h:
                        e['dates'] = str(next_dow(w, d=today))

            # Handling times
            timestr = re.search(r'(.*?);', splits[-2]).group(1)
            if '-' not in timestr:
                e['times'] = [str(parse(timestr).time())]
            else:
                match = re.search(r'(.*?)-(.*)', timestr) # Need greedy: to reach end of string
                (a, b) = match.groups()
                if 'p' in b.lower():
                    a += 'pm'
                else:
                    a += 'am'
                e['times'] = [str(parse(a).time()), str(parse(b).time())]

            events.append(e)
    
    return events

def next_dow(weekday, d=datetime.date.today()):
    while weekdays[d.weekday()] != weekday:
        d += datetime.timedelta(1)
    return d