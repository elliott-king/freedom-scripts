import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse
from datetime import date

from scripts import dyn_upload

base = "https://www.nationalartsclub.org"
calendar = ""
payload = {"p": ".NET_Calendar", "view": "l5"}


def events(table=dyn_upload.DEV_EVENTS_TABLE):
    soup = BeautifulSoup(requests.get(base, params=payload).text, "html.parser")
    events_table = soup.find("table", id="masterPageUC_MPCA399840_ctl06_listTable")

    last_date = str(date.today())
    events = []

    for row in events_table.find_all("tr"):
        if (
            row.find(class_="modCalWeekDayHeader")
            and row.find(class_="modCalWeekDayHeader").text
        ):
            last_date = str(parse(row.find(class_="modCalWeekDayHeader").text).date())
        if row.find(class_="modCalWeekRow") and row.find(class_="modCalWeekRow").text:
            is_free_event = True
            event = {
                "source": "The National Arts Club",
                "location_description": "15 Gramercy Park S, New York, NY",
                "host": "The National Arts Club",
                "rsvp": True,
                "dates": [last_date],
                "times": [],
            }
            for td in row.find_all("td"):
                if td.text.strip():
                    # td is either a time or a description
                    if " PM" in td.text or " AM" in td.text:
                        if "-" in td.text:
                            times = td.text.split("-")
                            for t in times:
                                event["times"].append(str(parse(t).time()))
                        else:
                            event["times"] = [str(parse(td.text).time())]
                    else:
                        if not td.a:
                            print(td.text)
                        event["website"] = td.a.get("href")
                        event["name"] = td.a.text

                        # The event page is a mess.
                        event_soup = BeautifulSoup(
                            requests.get(event["website"]).text, "html.parser"
                        )
                        event_soup = event_soup.find("div", id="eventData").find(
                            "div", id="eventData"
                        )
                        for script in event_soup(["script", "style"]):
                            script.decompose()

                        event_text = event_soup.text.lower()
                        if " rsvp" not in event_text or " free " not in event_text:
                            is_free_event = False
                        if event_soup.img:
                            event["photos"] = [event_soup.img.get("src")]
            if is_free_event and not dyn_upload.is_uploaded(event, table):
                events.append(event)
    return events
