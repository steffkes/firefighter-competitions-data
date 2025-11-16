from util import (
    Spider,
    ParticipantItem,
    ResultItem,
    ResultRankItem,
    JsonLinesItemExporter,
)
import scrapy
import re


# we need aggregated results to determine the total rank
class CustomExporter(JsonLinesItemExporter):
    def finish_exporting(self):
        sortedDuration = sorted(map(lambda item: item["duration"], self.items))

        def mapFn(item):
            item["rank"]["total"] = sortedDuration.index(item["duration"]) + 1
            return item

        self.items = list(map(mapFn, self.items))

        super().finish_exporting()


class CompetitionSpider(Spider):
    name = __name__
    race_id = "315247"
    race_key = "7e4105dee620c764485e85a405c3988f"

    # extend global spider config
    custom_settings = Spider.custom_settings
    custom_settings["FEED_EXPORTERS"]["results"] = CustomExporter

    @staticmethod
    def fixName(name):
        return " ".join(reversed(name.split(", ")))

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "rr Timing|Teilnehmerliste_Feuerwehrlauf",
                "contest": "0",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Ergebnisse|Ergebnisliste_Feuerwehr_Mixed",
                "contest": "1",
                "f": "Wertung: Fireheroes Leonberg",
            },
            cb_kwargs={
                "category": "X",
            },
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Ergebnisse|Ergebnisliste_Feuerwehr_MW",
                "contest": "1",
                "f": "Wertung: Fireheroes LeonbergMännlich",
            },
            cb_kwargs={"category": "M", "key": "#1_Männlich"},
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Ergebnisse|Ergebnisliste_Feuerwehr_MW",
                "contest": "1",
                "f": "Wertung: Fireheroes LeonbergWeiblich",
            },
            cb_kwargs={"category": "W", "key": "#2_Weiblich"},
        )

    def parse_starters(self, response):
        for [
            _id1,
            _id2,
            _origin,
            name1,
            name2,
            _yob1,
            _yob2,
            _gender,
        ] in response.json()["data"]["#1_Feuerwehrlauf"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted([name1, name2]),
            )

    def parse(self, response, category, key=None):
        data = response.json()["data"]["#1_Wertung: Fireheroes Leonberg"]

        if key:
            data = data[key]

        for team, results in data.items():
            [rank_category, raw_duration] = re.match(
                r"\#\d+_(\d+)\.///.*?///(.+)", team
            ).group(1, 2)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                duration=self.fixDuration(raw_duration),
                # results = [ [_, _, name, _, _], [_, _, name, _, _] ]
                names=sorted(map(lambda result: self.fixName(result[2]), results)),
                category=category,
                rank=ResultRankItem(
                    category=int(rank_category),
                ),
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Schimmer, Astrid", "Astrid Schimmer"),
        ("Bartholomä, Meike", "Meike Bartholomä"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
