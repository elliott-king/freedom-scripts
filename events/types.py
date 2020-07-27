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

def add_type(event, typename, strings, extra_search=[]):
    type_in_event = False
    for s in strings:
        if s in event['name'].lower() or ('description' in event and s in event['description'].lower()):
            type_in_event = True
    if type_in_event and 'types' in event and typename not in event['types']:
        event['types'].append(typename)

def add_rsvp(event):
  # rsvp?
  event['rsvp'] = False
  for s in ['rsvp', 'regist', 'sign-up', 'ticket', 'reserve', 'appointment`']:
      if s in event['name'].lower() or ('description' in event and s in event['description'].lower()):
          event['rsvp'] = True
  if 'description' in event and 'no registr' in event['description'].lower():
      event['rsvp'] = False
  

def add_types(event):
  # TODO: add 'omit' argument
  # TODO: Some types our users may not be initially interested in:
  # family, teen, education, senior, crafts, games, technology

  # TODO: if has type film, remove other types?

  add_type(event, 'family', ['toddler', 'preschool', 'baby', 'babies', 'child', 'family', 'pre-school', 'families', 'kids', 'toys', 'story time', 'storytime', 'pre-k', 'open play', ' stem ', 'youngster', 'kidz', 'parent', 'early literacy'])
  add_type(event, 'music', ['jazz', 'music', 'song', 'concert', 'opera', 'baroque', 'fugue', 'choral', 'quartet', 'karaoke'])
  add_type(event, 'film', ['film', 'movie', 'matinee', 'cinema', 'screening'])
  add_type(event, 'crafts', ['craft', 'coloring', 'knitting', 'sculpt', 'creative writing', 'sewing', 'materials', 'crochet', 'button', 'collage', 'felt ', 'perler', 'origami', 'supplies', 'beads', 'jewelry', 'create your own'])
  add_type(event, 'games', ['jigsaw', 'puzzle', 'boardgame', 'video games', 'card game', 'dungeons & dragons', 'gaming', 'ps4', 'nintendo switch', 'xbox', 'game', 'crossword', ' uno', 'lego ', 'legos', 'mah jong', 'mahjong', 'chess', 'wii', 'scrabble', 'bingo'])
  add_type(event, 'advocacy', ['awareness', 'council member', 'citizenship'])
  add_type(event, 'science', [' stem ', 'robot', ' steam '])
  add_type(event, 'technology', [])
  add_type(event, 'literature', ['literature', 'book discussion', 'book club', 'poem', 'poetry', 'reading and discussion', 'read and discuss'])
  # Tech things are really all classes: eg, learn CSS
  add_type(event, 'education', ['learn how to', 'learn to', 'teach you', 'edit text', 'practice', 'research', 'job application', 'tutor', 'education', 'covers the basics', 'cover the basics', 'computer', 'css', 'html', 'technolog', 'blogging', 'edit text', 'tech issue', 'bilingual', 'photoshop', 'job seeker', 'resume build', 'application', 'microsoft', 'downloading', 'intro to', 'introduction to', 'your resume', 'job search', 'career', 'database', 'excel genius', 'census', 'classroom', 'writer\'s circle'])
  add_type(event, 'health_medical', ['hygiene', 'mental health', 'first aid', 'disease', 'healthcare', 'health care', 'medical', 'wellness'])
  add_type(event, 'senior', [' aging', 'seniors', 'aarp'])
  add_type(event, 'athletics', ['athletics', 'exercise', 'fitness', 'physique', 'aerobics', 'sports', 'yoga'])
  add_type(event, 'teen', ['teen', 'tween', 'homework', 'student', 'college', 'manga', 'anime', 'youth'])
  add_type(event, 'history', ['history', 'historic'])
  add_type(event, 'comedy', ['comed'])

  # TODO: 'all ages'
  def check_age_range(start, end):
      start = int(start)
      if start < 11:
          if 'family' not in event['types']:
              event['types'].append('family')
      elif end:
          end = int(end)
          if end < 19:
              if 'teen' not in event['types']:
                  event['types'].append('teen')
      else:
          if 'teen' not in event['types']:
              event['types'].append('teen')


  # Attempt to parse an age range, if it exists
  if 'family' not in event['types'] and 'teen' not in event['types'] and 'description' in event:
      m = re.search(r'([0-9]+).+?([0-9]+)', event['description'])
      if m:
          check_age_range(m.group(1), m.group(2))
      else:
          m = re.search(r'ges ([0-9]+) and older', event['description'])
          if m:
              check_age_range(m.group(1), None)
          else:
              m = re.search(r'ges ([0-9]+) and up', event['description'])
              if m:
                  check_age_range(m.group(1), None)
              else:
                  m = re.search(r'ges ([0-9]+)[\s]?\+', event['description'])
                  if m:
                      check_age_range(m.group(1), None)
                  else:
                      m = re.search(r'ges ([0-9]+) &', event['description'])
                      if m:
                          check_age_range(m.group(1), None)

