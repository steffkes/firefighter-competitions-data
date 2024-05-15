import scrapy
from datetime import datetime


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]

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
            url="https://runtix.com/sts/10050/2413/oldies_erg/total/-",
            cb_kwargs={"competition_type": "MPA", "category": "M"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://runtix.com/sts/10050/2413/young_erg/total/-",
            cb_kwargs={"competition_type": "MPA", "category": "M"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://runtix.com/sts/10050/2413/ladies_erg/total/-",
            cb_kwargs={"competition_type": "MPA", "category": "W"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://runtix.com/sts/10050/2413/mix_erg/total/-",
            cb_kwargs={"competition_type": "MPA", "category": "X"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://runtix.com/sts/10050/2413/mixo_erg/total/-",
            cb_kwargs={"competition_type": "OPA", "category": "X"},
        )

    def parse(self, response, competition_type, category):
        for row in response.css("table.results tbody tr"):
            bib = row.css(".col-number div::text").get()
            duration = row.css(".col-net-time a::text").get()

            if duration == "DISQ":  # disqualified
                continue

            [lastname1, firstname1, lastname2, firstname2] = map(
                str.strip, row.css(".col-competitor div::text").get().split(",")
            )

            yield {
                "date": self.race_date,
                "competition_id": self.competition_id,
                "bib": bib,
                "type": competition_type,
                "duration": duration,
                "catgory": category,
                "names": sorted(
                    [
                        "%s %s" % (firstname1, lastname1),
                        "%s %s" % (firstname2, lastname2),
                    ]
                ),
            }
