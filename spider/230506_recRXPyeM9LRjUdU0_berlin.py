import scrapy
from datetime import datetime
from pathlib import Path
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)

nameMappings = {}


class Spider(scrapy.spiders.CSVFeedSpider):
    name = __name__
    race_date = datetime.strptime(__name__.split("_")[0], "%y%m%d").strftime("%Y-%m-%d")
    competition_id = __name__.split("_")[1]
    ident = __name__[0:24]

    delimiter = ";"

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
            url="https://www.ergebnisliste.de/urkunden/urkstairrun_suche_nach_kombi.php",
            callback=self.parse,
        )

    def parse(self, response):
        results = []
        for row in filter(
            lambda row: row.css(":nth-child(4)::text").get() == "Stairrun"
            and row.css(".datum::text").get() == "06.05.2023",
            response.css("table tr"),
        ):
            duration = "00:" + ("0" + row.css(":nth-child(9)::text").get())[-7:]
            age_group = row.css(":nth-child(8)::text").get()
            names = row.css(":nth-child(12)::text").get().split("/")

            result = ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="MPA",
                duration=duration,
                category={"Ladies": "W", "Mix": "X"}.get(age_group, "M"),
                age_group=age_group,
                names=sorted(map(fixName, names)),
                bib=row.css(":nth-child(5)::text").get(),
                rank=ResultRankItem(
                    total=int(row.css(":nth-child(11)::text").get()),
                    age_group=int(row.css(":nth-child(10)::text").get()),
                ),
            )

            if result["category"] in ["W", "X"]:
                del result["age_group"]
                del result["rank"]["age_group"]

            results.append(result)

        results = sorted(results, key=lambda result: result["duration"])

        for category in sorted(set(map(lambda result: result["category"], results))):
            results_category = list(
                filter(lambda result: result["category"] == category, results)
            )
            durations_category = list(
                map(lambda result: result["duration"], results_category)
            )

            for result in results_category:
                result["rank"]["category"] = (
                    durations_category.index(result["duration"]) + 1
                )
                yield result


def fixName(name):
    fixed = " ".join(map(str.strip, reversed(name.split(","))))

    return nameMappings.get(fixed, fixed)


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Süßenbach, Jan ", "Jan Süßenbach"),
        (" Di Gioia, Alessandro ", "Alessandro Di Gioia"),
        ("Grote-Lambers, Katrin-Madlen", "Katrin-Madlen Grote-Lambers"),
        ("Tuchbreiter,Nicole", "Nicole Tuchbreiter"),
    ],
)
def test_fixName(input, output):
    assert fixName(input) == output
