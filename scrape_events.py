from dotenv import load_dotenv
# Run before script imports to load env vars
load_dotenv()

from freedom.events.locations import queens_library
from freedom.events import user_input


# to write to a logfile, use `python3 -u scrape_events > file`
if __name__ == '__main__':

  # pylint: disable=undefined-variable
  sources = {
    # "Bric Arts Media": bric_arts,
    # "Bluestockings": bluestockings,
    # "Brooklyn Library": brooklyn_library,
    "Queens Library": queens_library,
    # "NYPL": nypl,
  }
  # pylint: enable=undefined-variable

  events = []
  for source in sources:
    print("Now parsing: ", source)
    source_events = sources[source].events()
    print("Number of events from " + source + ":", len(source_events))
    events += source_events

  user_input.upload_multiple_with_skips(events)
  print("Total number of events:", len(events))