import scrapy
from datetime import datetime
from itertools import groupby
from util import (
    JsonItemExporter,
    JsonLinesItemExporter,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
)
from pathlib import Path
import pandas as pd
from io import StringIO
import copy


class TfaResultItem(ResultItem):
    country = scrapy.Field()


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
        yield scrapy.Request(
            "file://%s"
            % Path(
                "spider/data/240608_recUBqaMJOOe95CEW_moenchengladbach_individual.txt"
            ).resolve(),
            callback=self.parse_individual,
        )

        yield scrapy.Request(
            "file://%s"
            % Path(
                "spider/data/240608_recUBqaMJOOe95CEW_moenchengladbach_relay.txt"
            ).resolve(),
            callback=self.parse_relay,
        )

    def parse_individual(self, response):
        df = pd.read_fwf(StringIO(response.body.decode("utf-8")))

        results = []
        for index, row in df.iterrows():
            results.append(
                TfaResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    duration=row["Zeit gesamt"] + ".0",
                    type="OPA",
                    names=["{Vorname} {Name}".format(**row)],
                    category="%s individual" % row["M/W"],
                    age_group=row["Altersklasse"],
                    bib=str(row["BIB"]),
                    country=row["Land"],
                )
            )

        def handler(results, label):
            durations = sorted(map(lambda result: result["duration"], results))

            for category, age_group in sorted(
                set(
                    map(
                        lambda result: (result["category"], result["age_group"]),
                        results,
                    )
                )
            ):
                results_category = list(
                    filter(lambda result: result["category"] == category, results)
                )
                results_age_group = list(
                    filter(
                        lambda result: result["age_group"] == age_group,
                        results_category,
                    )
                )

                durations_category = sorted(
                    map(lambda result: result["duration"], results_category)
                )
                durations_age_group = sorted(
                    map(lambda result: result["duration"], results_age_group)
                )

                for result in results_age_group:
                    result["rank"] = ResultRankItem(
                        total=durations.index(result["duration"]) + 1,
                        category=durations_category.index(result["duration"]) + 1,
                        age_group=durations_age_group.index(result["duration"]) + 1,
                    )

                    result["category"] = "%s (%s)" % (result["category"], label)
                    del result["country"]

                    yield result

        yield from handler(copy.deepcopy(results), "EU")
        yield from handler(
            list(
                filter(
                    lambda result: result["country"] == "DEU", copy.deepcopy(results)
                )
            ),
            "DE",
        )

    def parse_relay(self, response):
        df = pd.read_fwf(StringIO(response.body.decode("utf-8")))

        results = []
        for index, row in df.iterrows():
            results.append(
                TfaResultItem(
                    date=self.race_date,
                    competition_id=self.competition_id,
                    duration=row["Staffel gesamt"] + ".0",
                    type="OPA",
                    names=sorted(
                        [
                            row["1. Starter"],
                            row["2. Starter"],
                            row["3. Starter"],
                            row["4. Starter"],
                        ]
                    ),
                    category="%s relay"
                    % {"Male": "M", "Mixed": "X"}.get(row["StaffelTyp"]),
                    bib=str(row["BIB"]),
                    country=row["Land"],
                )
            )

        def handler(results, label):
            durations = sorted(map(lambda result: result["duration"], results))

            for category in sorted(
                set(
                    map(
                        lambda result: result["category"],
                        results,
                    )
                )
            ):
                results_category = list(
                    filter(lambda result: result["category"] == category, results)
                )

                durations_category = sorted(
                    map(lambda result: result["duration"], results_category)
                )

                for result in results_category:
                    result["rank"] = ResultRankItem(
                        total=durations.index(result["duration"]) + 1,
                        category=durations_category.index(result["duration"]) + 1,
                    )

                    result["category"] = "%s (%s)" % (result["category"], label)
                    del result["country"]

                    yield result

        yield from handler(copy.deepcopy(results), "EU")
        yield from handler(
            list(
                filter(
                    lambda result: result["country"] == "DEU", copy.deepcopy(results)
                )
            ),
            "DE",
        )
