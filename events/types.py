import re

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

def rsvp(description):
    if 'no registr' in description.lower():
        return False
    for s in ['rsvp', 'regist', 'sign-up', 'ticket', 'reserve', 'appointment']:
        if s in description.lower():
            return True
    return False

def check_type(description, typename, strings):
    for s in strings:
        if s in description.lower():
            return True
    return False

def types(name='', description=''):
    # TODO: add 'omit' argument
    # TODO: Some types our users may not be initially interested in:
    # family, teen, education, senior, crafts, games, technology

    # TODO: if has type film, remove other types?
    description = name + ' ' + description
    ret = []

    types = {
        'advocacy': ['awareness', 'council member', 'citizenship'],
        'athletics': ['athletics', 'exercise', 'fitness', 'physique', 'aerobics', 'sports', 'yoga'],
        'comedy': ['comed'],
        'crafts': ['craft', 'coloring', 'knitting', 'sculpt', 'creative writing', 'sewing', 'materials', 'crochet', 'button', 'collage', 'felt ', 'perler', 'origami', 'supplies', 'beads', 'jewelry', 'create your own'],
        # Tech things are really all classes: eg, learn CSS
        'education': ['learn how to', 'learn to', 'learn mo', 'learn the ', 'teach you', 'edit text', 'practice', 'research', 'job application', 'tutor', 'education', 'covers the basics', 'cover the basics', 'computer', 'css', 'html', 'technolog', 'blogging', 'edit text', 'tech issue', 'bilingual', 'photoshop', 'job seeker', 'resume build', 'application', 'microsoft', 'downloading', 'intro to', 'introduction to', 'your resume', 'job search', 'career', 'database', 'excel genius', 'census', 'classroom', 'writer\'s circle'],
        'family': ['toddler', 'preschool', 'baby', 'babies', 'child', 'family', 'pre-school', 'families', 'kids', 'toys', 'story time', 'storytime', 'pre-k', 'open play', ' stem ', 'youngster', 'kidz', 'parent', 'early literacy'],
        'film': ['film', 'movie', 'matinee', 'cinema', 'screening'],
        'games': ['jigsaw', 'puzzle', 'boardgame', 'video games', 'card game', 'dungeons & dragons', 'gaming', 'ps4', 'nintendo switch', 'xbox', 'game', 'crossword', ' uno', 'lego ', 'legos', 'mah jong', 'mahjong', 'chess', 'wii', 'scrabble', 'bingo'],
        'health_medical': ['hygiene', 'mental health', 'first aid', 'disease', 'healthcare', 'health care', 'medical', 'wellness'],
        'history': ['history', 'historic'],
        'literature': ['literature', 'book discussion', 'book club', 'poem', 'poetry', 'reading and discussion', 'read and discuss', 'story discus', 'stories discus', 'book talk'],
        'music': ['jazz', 'music', 'song', 'concert', 'opera', 'baroque', 'fugue', 'choral', 'quartet', 'karaoke'],
        'science': [' stem ', 'robot', ' steam '],
        'senior': [' aging', 'seniors', 'aarp'],
        'technology': [],
        'teen': ['teen', 'tween', 'homework', 'student', 'college', 'manga', 'anime', 'youth', 'young adult'],
        'theater': ['theater', 'theatre', 'acting'],
    }
    for t, strings in types.items():
        if check_type(description, t, strings):
            ret.append(t)
    
    family_type = check_family_events(description)
    if family_type and family_type not in ret:
        ret.append(family_type)
    return ret


def check_family_events(description):
    # TODO: 'all ages',
    def check_age_range(start, end):
        start = int(start)
        if start < 11:
            return 'family'
        elif end:
            end = int(end)
            if end < 19:
                return 'teen'
        else:
            return 'teen'


  # Attempt to parse an age range, if it exists
        m = re.search(r'([0-9]+).+?([0-9]+)', description)
        if m:
            return check_age_range(m.group(1), m.group(2))
        else:
            m = re.search(r'ges ([0-9]+) and older', description)
            if m:
                return check_age_range(m.group(1), None)
            else:
                m = re.search(r'ges ([0-9]+) and up', description)
                if m:
                    return check_age_range(m.group(1), None)
                else:
                    m = re.search(r'ges ([0-9]+)[\s]?\+', description)
                    if m:
                        return check_age_range(m.group(1), None)
                    else:
                        m = re.search(r'ges ([0-9]+) &', description)
                        if m:
                            return check_age_range(m.group(1), None)
    return False
