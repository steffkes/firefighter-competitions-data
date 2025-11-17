import scrapy
import itertools
from datetime import datetime
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)


class Spider(scrapy.Spider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    race_id = 369334
    race_key = "e4c56a94b55a61d6f4cfabd9759bb48e"

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
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "02_Teilnehmerlisten|Teilnehmer_Schanzenlauf",
                "contest": "1",
            },
            callback=self.parse_starters,
        )

        """
        for selector in range(1, 10):
            yield scrapy.FormRequest(
                method="GET",
                url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
                formdata={
                    "key": self.race_key,
                    "listname": "01 - Online|Results",
                    "contest": "1",
                    "page": "results",
                    "selectorResult": str(selector),
                },
                cb_kwargs={
                    "ranks": {9: {0: 1, 1: 2}, 8: {0: 3}}.get(selector, {}),
                },
            )
        """

    def parse_starters(self, response):
        for [[_bib, _id, name1, name2]] in (response.json()["data"] or {}).values():
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted([name1, name2]),
            )

    def parse(self, response, ranks):
        for index, [
            bib,
            rank,
            _bib,
            names,
            _team,
            _q,
            raw_duration,
            _diff,
            _cert,
            _cert_link,
        ] in enumerate(itertools.chain.from_iterable(response.json()["data"].values())):
            if rank == "DNF":
                continue

            result = ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration="00:0%s" % raw_duration[:-1].replace(",", "."),
                names=sorted(names.split(" & ")),
                bib=bib,
            )

            if index in ranks:
                result["rank"] = ResultRankItem(total=ranks.get(index))

            yield result
