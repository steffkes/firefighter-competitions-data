import scrapy
from datetime import datetime


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]

    race_id = 266311
    race_key = "bac6b526cf62ea3cc99afd4f707ac0cc"

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
            url="https://my.raceresult.com/%d/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "1",
                "listname": "10 Ergebnislisten|00 Ergebnisliste OA (Kategorie)",
            },
            cb_kwargs={
                "competition_type": "MPA",
            },
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%d/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "contest": "2",
                "listname": "10 Ergebnislisten|00 Ergebnisliste OA (Kategorie)",
            },
            cb_kwargs={
                "competition_type": "OPA",
            },
        )

    def parse(self, response, competition_type):
        for entry in response.json()["data"]:
            [_, status, bib, _, _, names, category, raw_duration, _] = entry

            if status == "DSQ":  # disqualified
                continue

            category = category.split(" ")[0]
            names = sorted(map(str.strip, names.split("|")))
            duration = "00:" + raw_duration.replace(",", ".")

            yield {
                "date": self.race_date,
                "competition_id": self.competition_id,
                "bib": bib,
                "type": competition_type,
                "duration": duration,
                "category": {
                    "Burschen": "M",
                    "Mannsbilder": "M",
                    "Alte": "M",
                    "Pärchen": "X",
                    "Mädels": "W",
                }[category],
                "names": names,
            }
