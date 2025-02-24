import scrapy
from datetime import datetime
import re


class ParticipantItem(scrapy.Item):
    competition_id = scrapy.Field()
    names = scrapy.Field()


class ResultRankItem(scrapy.Item):
    total = scrapy.Field()
    category = scrapy.Field()
    age_group = scrapy.Field()


class ResultItem(scrapy.Item):
    date = scrapy.Field()
    competition_id = scrapy.Field()
    duration = scrapy.Field()
    type = scrapy.Field()
    category = scrapy.Field()
    names = scrapy.Field()
    bib = scrapy.Field()
    age_group = scrapy.Field()
    rank = scrapy.Field()


from scrapy.utils.python import to_bytes
from scrapy.exporters import (
    BaseItemExporter,
    JsonLinesItemExporter as BaseJsonLinesItemExporter,
)
from scrapy.utils.serialize import ScrapyJSONEncoder
import itertools


class JsonItemExporter(BaseItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(dont_fail=True, **kwargs)

        self.file = file
        self.items = []

        self._kwargs.setdefault("indent", 2)
        self._kwargs.setdefault("ensure_ascii", not self.encoding)
        self.encoder = ScrapyJSONEncoder(**self._kwargs)

    def finish_exporting(self):
        if not len(self.items):
            return

        teams = sorted(
            map(lambda item: item["names"], self.items),
            key=lambda entry: (len(entry), entry),
        )
        data = {
            "date": datetime.now().isoformat(),
            "competition_id": self.items[0]["competition_id"],
            "count": len(list(itertools.chain.from_iterable(teams))),
            "teams": teams,
        }

        self.file.write(
            to_bytes(
                self.encoder.encode(data) + "\n",
                self.encoding,
            )
        )

    def export_item(self, item):
        self.items.append(item)


class JsonLinesItemExporter(BaseJsonLinesItemExporter):
    def __init__(self, file, **kwargs):
        super().__init__(file, **kwargs)

        self.items = []

    def export_item(self, item):
        self.items.append(item)

    def finish_exporting(self):
        results = sorted(
            self.items,
            key=lambda item: (
                item["duration"],
                item["type"],
                item.get("category"),
                item.get("age_group"),
                item.get("bib"),
            ),
        )

        self.file.write(
            to_bytes(
                "\n".join(map(self.encoder.encode, results)) + "\n",
                self.encoding,
            )
        )


class Spider(scrapy.Spider):
    ranks = {"category": {}, "age_group": {}}

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

    def __init__(self):
        self.race_date = datetime.strptime(self.name.split("_")[0], "%y%m%d").strftime(
            "%Y-%m-%d"
        )
        self.competition_id = self.name.split("_")[1]
        self.ident = self.name[0:24]

        super().__init__()

    @staticmethod
    def fixName(name):
        return name

    @staticmethod
    def fixDuration(duration):
        return re.sub(
            r"((\d+):)?(\d+):(\d+),(\d)\d*",
            lambda match: "{0:02d}:{1:02d}:{2:02d}.{3}".format(
                *map(lambda input: int(input or 0), match.group(2, 3, 4, 5))
            ),
            duration,
        )


class FirefitSpider(Spider):
    def parse(self, response):
        tables = response.css("table.ffc-table-dark")

        for index, (type, category) in enumerate(
            [
                ("MPA", "M individual"),
                ("MPA", "W individual"),
                ("OPA", "M tandem"),
                ("OPA", "W tandem"),
                ("OPA", "X tandem"),
                ("OPA", "M relay"),
                ("OPA", "W relay"),
                ("OPA", "X relay"),
            ]
        ):
            for row in tables[index].css("tbody tr.status-ok"):
                raw_duration = "".join(row.css(".result-line1 span::text").getall())

                names = [row.css(".name-line1::text").get().strip()]
                team = sorted(row.css(".member-name span::text").getall())
                if len(team):
                    names = team

                yield ResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    type=type,
                    duration=self.fixDuration(raw_duration),
                    names=names,
                    category=category,
                    rank=ResultRankItem(
                        category=int(
                            row.css(".rank-val.age-overall::text").get()[0:-1]
                        ),
                    ),
                )


import pytest


@pytest.mark.parametrize(
    "output,input",
    [
        ("00:13:31.6", "13:31,6"),
        ("01:00:27.0", "1:00:27,0"),
        ("00:05:48.3", "5:48,34"),
        ("00:02:55.7", "2:55,70"),
        ("00:02:46.9", "2:46,96"),
    ],
)
def test_fixDuration(input, output):
    assert Spider.fixDuration(input) == output
