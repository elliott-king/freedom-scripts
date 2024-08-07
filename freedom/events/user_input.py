from dateutil.parser import parse
from datetime import timedelta
from collections import defaultdict

from freedom.scripts import dyn_upload
from freedom.events.models import Event
from freedom.events.utils import write_to_debug_file

multi_fields = ["dates", "times"]

title_fields = ["name", "host", "location_description"]

single_fields = [
    "website",
    "description",
    "rsvp",
    "source",
    # Omit 'location', need Google for that.
    # omit photos?
]

IN_QUARANTINE = False


class SkipEventError(Exception):
    """Signify that user would like to skip this event."""

    def __init__(self, message):
        self.message = message


# def upload_multiple_no_overview(events):
#     for i, e in enumerate(events):
#         print('on item', i, 'of', len(events))
#         if not check_filled(e):
#             raise SkipEventError('Event ' + str(i) + ' not filled:' + str(e))
#         if check_canceled(e):
#             raise SkipEventError('Event ' + str(i) + ' is cancelled:' + str(e))
#         if 'website' in e and 'http' not in e['website']:
#             e['website'] = 'http://' + e['website']
#         if 'location' not in e:
#             e['location'] = search_one(e['location_description'])

#     dyn_upload.add_items_to_table(dyn_upload.DEV_EVENTS_TABLE, dyn_upload.DEV_PHOTOS_TABLE, events)  # noqa: E501


def upload_multiple_with_skips(events: list[Event]):
    finalized_events = []
    for i, e in enumerate(events):
        e.validate()

        if e.cancelled():
            print()
            print(f"Event {i} is cancelled: {e}")
            continue

        e.finalize()
        finalized_events.append(e)

    write_to_debug_file(finalized_events)
    dyn_upload.add_items_to_table(
        dyn_upload.DEV_EVENTS_TABLE, dyn_upload.DEV_PHOTOS_TABLE, finalized_events
    )

    #     if not check_filled(e):
    #         print()
    #         print('Event ' + str(i) + ' not filled:' + str(e))
    #         continue
    #     if check_canceled(e):
    #         print()
    #         print('Event ' + str(i) + ' is cancelled:' + str(e))
    #         continue
    #     if 'website' in e and 'http' not in e['website']:
    #         e['website'] = 'http://' + e['website']
    #     if 'location' not in e:
    #         e['location'] = places_api_search_one(e['location_description'])
    #     finalized_events.append(e)
    # write_to_debug_file(events)
    # dyn_upload.add_items_to_table(dyn_upload.DEV_EVENTS_TABLE, dyn_upload.DEV_PHOTOS_TABLE, finalized_events)  # noqa: E501


# def request_multiple(events):
#     # TODO: re-request the database events to check against for dupes
#     for i, e in enumerate(events):
#         print('on item', i, 'of', len(events))
#         request_input(e)

# should create new dict
# def request_input(d):
#     print('=' * 40)
#     if 'website' in d and len(d['website']) < 6:
#         # Throw out garbage
#         del d['website']
#     if check_canceled(d):
#         return
#     display_missing(d)
#     if 'id' in d:
#         del d['id']
#     if IN_QUARANTINE:
#         if not d['location_description']:
#             d['location_description'] = 'Manhattan'
#     try:
#         display_info(d)
#         singleton_fields(d)

#         apply_dates(d)
#         apply_times(d)

#         if 'location' not in d:
#             d['location'] = places_api_search_one(d['location_description'])

#         pprint.pprint(d)

#         if not check_filled(d):
#             print ('Not uploading.')
#             return
#         if 'website' in d and 'http' not in d['website']:
#             d['website'] = 'http://' + d['website']
#         upload = get_user_input('Upload (Y/n)? ')
#         if upload in ['n', 'N', 'no', 'No', 'NO']:
#             print('Did not upload')
#         else:
#             # TODO: should choose table
#             dyn_upload.add_items_to_table(dyn_upload.DEV_EVENTS_TABLE, dyn_upload.DEV_PHOTOS_TABLE, [d])  # noqa: E501

#     except SkipEventError:
#         print('Skipping this event')
#     except Exception:
#         print(traceback.format_exc())
#         print('Issue with information, NOT UPLOADING')


def display_missing(d):
    missing = []
    for f in single_fields + title_fields:
        if f not in d:
            missing.append(f)
            d[f] = None
    for f in multi_fields:
        if f not in d:
            missing.append(f)
            d[f] = []
    print("Expected but did not find:", missing)


# def check_canceled(d):
#     for field in ['name', 'description']:
#         if field in d and d[field]:
#             if 'canceled' in d[field].lower() or 'cancelled' in d[field].lower():
#                 print("Event canceled:", d['name'])
#                 return True
#     return False


def display_info(d):
    print("Text:")
    print(d["description"])
    if "website" in d:
        print(d["website"], "\n")


# def singleton_fields(d):
#     for f in d:
#         if f not in multi_fields:
#             print(f.upper(), ":", " " * (20 - len(f)), d[f])
#             new = get_user_input("If applicable, new value:\n")
#             if new and new != "yes" and new != "y" and new != "Y" and new != "Yes":
#                 d[f] = new
#                 if f.lower() == "rsvp":
#                     d[f] = d[f] == "True"
#             if f in title_fields:
#                 d[f] = titlecase(d[f])

#     try:
#         j = r.json()["candidates"][0]  # first result probably correct
#     except IndexError:
#         raise TypeError("No location found: ", name)

#     location = {
#         "lat": j["geometry"]["location"]["lat"],
#         "lon": j["geometry"]["location"]["lng"],
#     }
#     return location


def apply_times(d):
    print("times:", d["times"])
    times = []
    while True:
        new = get_user_input("Enter a time, or refuse: ")
        if new and new != "yes" and new != "y" and new != "Y" and new != "Yes":
            times.append(str(parse(new).time()))
        else:
            break
    if times:
        d["times"] = times


def apply_dates(d):
    # TODO: some nypl events have multiple times w/in one day
    d["dates"] = list(set(d["dates"]))
    print("dates:", d["dates"])
    dates = []
    while True:
        new = get_user_input("Enter a date, or refuse: ")
        if new and new != "yes" and new != "y" and new != "Y" and new != "Yes":

            # date range should be user-formatted start,end
            if "," in new:
                [s, e] = new.split(",")
                print(s, e)
                s = parse(s).date()
                e = parse(e).date()
                print(s, e)
                arr = [str(s + timedelta(days=x)) for x in range(0, (e - s).days + 1)]
                print(arr)
                dates += arr
            else:
                dates.append(
                    str(parse(new).date())
                )  # user should write in year, if it is next year
        else:
            break
    if dates:
        d["dates"] = dates


# legacy & unused
def apply_types(d):
    print("types:", d["types"])
    types = []
    while True:
        new = get_user_input("Enter a type, or refuse: ")
        if new and new != "yes" and new != "y" and new != "Y" and new != "Yes":
            types.append(new)
        else:
            break
    if types:
        d["types"] = types


# def check_filled(d):
#     error_str = 'Expecting value for field:'
#     for f in multi_fields:
#         if f not in d or not isinstance(d[f], list):
#             print(error_str, f)
#             return False
#     for f in title_fields:
#         if f not in d or not d[f]:
#             print(error_str, f)
#     for f in single_fields:
#         if f not in ['description', 'rsvp']:
#             if f not in d or not d[f]:
#                 print(error_str, f)
#                 return False
#         elif f not in d:
#             print(error_str, f)
#             return False
#     return True


def get_user_input(s):
    i = input(s)
    if i and i == "skip":
        raise SkipEventError("Skip this event.")
    return i


# In the interest of making my work simpler, and making this more presentable where I am putting up
# the events (namely reddit), we can identify the family-oriented events and set them aside.
def reddit_oriented(event):
    for t in ["family", "teen", "senior", "crafts", "games", "technology"]:  # education
        if t in event["types"]:
            print("Event is family event, has type:", t)
            return False
    return True


# events that have the same name should be merged, with their dates & times added together
# after quarantine, may be good to enforce that events also have the same location_description
def squash_events(events):
    ret = []
    events_by_name = defaultdict(list)
    for e in events:
        events_by_name[e["name"]].append(e)

    for _event_name, list_by_name in events_by_name.items():
        if len(list_by_name) == 1:
            ret.append(list_by_name[0])
            continue
        combined_event = list_by_name[0]
        for shared_event in list_by_name[1:]:
            combined_event["dates"] = sorted(
                list(set(combined_event["dates"] + shared_event["dates"]))
            )
            combined_event["times"] += shared_event["times"]
        ret.append(combined_event)
    return ret
