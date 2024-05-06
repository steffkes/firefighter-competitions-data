import scrapy
from datetime import datetime


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]

    race_id = "176815"
    race_key = "f85c774317152b6fcd49105b79cdc884"

    custom_settings = {
        "FEEDS": {
            "data/teams/%(name)s.jsonl": {
                "format": "jsonlines",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
    }

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "5",
                "listname": "02 - Ergebnislisten|Zieleinlaufliste",
            },
            cb_kwargs={
                "competition_type": "MPA",
                "data_key": "#1_Feuerwehr PA",
            },
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "6",
                "listname": "02 - Ergebnislisten|Zieleinlaufliste",
            },
            cb_kwargs={
                "competition_type": "OPA",
                "data_key": "#1_Feuerwehr",
            },
        )

    def parse(self, response, data_key, competition_type):
        for entry in response.json()["data"][data_key]:
            [_, _, bib, names, category, _, raw_duration] = entry

            [category, _] = category.split(" ")
            names = sorted(map(str.strip, names.split("/")))
            duration = "00:%s.0" % raw_duration.zfill(5)

            yield {
                "date": self.race_date,
                "competition_id": self.competition_id,
                "bib": bib,
                "type": competition_type,
                "duration": duration,
                "category": {"MIX": "X"}.get(category, category),
                "names": names,
            }
