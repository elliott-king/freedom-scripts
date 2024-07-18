from dotenv import load_dotenv

# Run before script imports to load env vars
load_dotenv()

# to write to a logfile, use `python3 -u scrape_events > file`
if __name__ == "__main__":

    from freedom.events.locations import queens_library
    from freedom.events import user_input

    sources = {
        # "Bric Arts Media": bric_arts,
        # "Bluestockings": bluestockings,
        # "Brooklyn Library": brooklyn_library,
        "Queens Library": queens_library,
        # "NYPL": nypl,
    }

    events = []
    for s, source in sources.items():
        print("Now parsing: ", s)
        source_events = source.events()
        print("Number of events from " + s + ":", len(source_events))
        events += source_events

    user_input.upload_multiple_with_skips(events)
    print("Total number of events:", len(events))
