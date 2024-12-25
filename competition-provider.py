from itertools import repeat
from pathlib import Path
import pandas as pd
import requests
import json
import os


def loaderFn(path):
    try:
        with path.open() as handle:
            data = json.load(handle)
            return [data["competition_id"], data["count"]]
    except:
        return None


participantsCount = dict(
    filter(None, map(loaderFn, Path("data/participants").glob("*.json")))
)


def mapperFn(record, kind):
    coordinates = None

    if tmpCoordinates := record["fields"].get("Koordinaten"):
        [lat, lng] = tmpCoordinates.split(",")
        coordinates = {"lat": float(lat), "lng": float(lng)}

    return {
        "id": record["id"],
        "kind": kind,
        "name": record["fields"]["Name"],
        "url": record["fields"].get("Webseite"),
        "participants": {
            "count": participantsCount.get(record["id"]),
        },
        "date": {
            "start": record["fields"]["Datum"],
            "end": record["fields"].get("Datum bis") or record["fields"]["Datum"],
            "is_draft": record["fields"].get("Vorläufig"),
            "is_canceled": record["fields"].get("Abgesagt"),
            "registration_opens": record["fields"].get("Anmeldestart"),
        },
        "location": {
            "city": record["fields"].get("Ort"),
            "country_code": record["fields"].get("Land"),
            "coordinates": coordinates,
        },
    }


stairruns = requests.get(
    "https://api.airtable.com/v0/appF8BPHzWCy6OKVF/tbl7nlGCJYqn3uF7C",
    headers={
        "Authorization": "Bearer " + os.environ["AIRTABLE_API_KEY"],
    },
).json()["records"]

challenges = requests.get(
    "https://api.airtable.com/v0/appF8BPHzWCy6OKVF/tblRWTfwwmzoImHq1",
    headers={
        "Authorization": "Bearer " + os.environ["AIRTABLE_API_KEY"],
    },
).json()["records"]

dateFilterFn = lambda record: record["fields"].get("Datum")

competitions = sorted(
    list(map(mapperFn, filter(dateFilterFn, stairruns), repeat("FSR")))
    + list(map(mapperFn, filter(dateFilterFn, challenges), repeat("FCC"))),
    key=lambda record: record["date"]["start"],
)

with open("data/competitions.json", "w") as handle:
    json.dump(competitions, handle, ensure_ascii=False, indent=4)
