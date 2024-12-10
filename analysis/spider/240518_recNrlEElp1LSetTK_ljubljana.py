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
            "../data/teams/%(ident)s.json": {
                "format": "starter",
                "encoding": "utf8",
                "overwrite": True,
                "item_classes": [ParticipantItem],
            },
            "data/teams/%(name)s.jsonl": {
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
        for contest, type, gender in [
            ("G1M", "MPA", "M"),  # single male
            ("G1Z", "MPA", "W"),  # single female
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://remote.timingljubljana.si/stepup/Rezultati.aspx",
                formdata={"cat": contest},
                callback=self.parse_single,
                cb_kwargs={"type": type, "gender": gender},
            )

        for contest, type in [
            ("G3", "OPA"),  # relay mixed
            ("GE", "MPA"),  # relay mixed
        ]:
            yield scrapy.FormRequest(
                method="GET",
                url="https://remote.timingljubljana.si/stepup/Rezultati.aspx",
                formdata={"cat": contest},
                callback=self.parse_relay,
                cb_kwargs={"type": type},
            )

    def parse_single(self, response, type, gender):
        for row in response.css("table tr")[1:]:
            [_, name, _country, _team, duration] = row.css("td ::text").getall()

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type=type,
                category=gender,
                duration="0" + duration,
                names=[name],
                bib=None,
            )

    def parse_relay(self, response, type):
        for row in response.css("table tr")[1:]:
            [
                _bib,
                names,
                _country,
                _team,
                duration1,
                duration2,
                duration3,
                _sum1_2,
                _sum,
            ] = row.css("td ::text").getall()

            for name, duration in zip(
                names.split(","), [duration1, duration2, duration3]
            ):
                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=type,
                    category=None,
                    duration="0" + duration,
                    names=[name.strip()],
                    bib=None,
                )
