import scrapy
from datetime import datetime
from util import JsonItemExporter, JsonLinesItemExporter, ParticipantItem, ResultItem


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    custom_settings = {
        "FEED_EXPORTERS": {
            "starter": JsonItemExporter,
            "results": JsonLinesItemExporter,
        },
        "FEEDS": {
            "data/participants/%(ident)s.json": {
                "format": "starter",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ParticipantItem],
            },
            "data/results/%(name)s.jsonl": {
                "format": "results",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ResultItem],
            },
        },
        "EXTENSIONS": {
            "scrapy.extensions.telnet.TelnetConsole": None,
        },
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

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                bib=bib,
                type=competition_type,
                duration=duration,
                category=category,
                names=sorted(
                    [
                        "%s %s" % (firstname1, lastname1),
                        "%s %s" % (firstname2, lastname2),
                    ]
                ),
            )
