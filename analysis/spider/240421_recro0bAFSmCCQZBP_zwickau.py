import scrapy
from datetime import datetime
import re


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]

    race_id = "275363"
    race_key = "2763c5212a432a43da74006d8553cbcb"

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
                "listname": "Ergebnislisten|Feuerwehr AK",
                "contest": "2",
            },
            cb_kwargs={"data_key": "#1_Feuerwehr-Treppenlauf-Zwickau"},
        )

    def parse(self, response, data_key):
        data = response.json()["data"]
        for entry in data[data_key]["#1_m"]["#1_"] + data[data_key]["#2_a"]["#2_"]:
            [bib, _, _, _, _, _, names, raw_duration] = entry

            names = sorted(list(map(str.strip, re.split(r"[/,]", names))))
            duration = "00:" + raw_duration.replace(",", ".")

            yield {
                "date": self.race_date,
                "competition_id": self.competition_id,
                "bib": bib,
                "type": "OPA",
                "duration": duration,
                "names": names,
            }
