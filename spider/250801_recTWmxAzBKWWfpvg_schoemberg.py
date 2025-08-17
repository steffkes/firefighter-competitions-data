import scrapy
from util import Spider, ParticipantItem, ResultItem
import re


class CompetitionSpider(Spider):
    name = __name__

    race_id = "314379"
    race_key = "5dfc4e446d96c06bd1addb9630b6273d"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "rr Timing|Teilnehmerliste_Feuerwehrlauf",
                "contest": "9",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Baywa und Feuerwehr|Ergebnisliste_Feuerwehr_MW",
                "contest": "9",
            },
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Baywa und Feuerwehr|Ergebnisliste_Feuerwehr_Mixed",
                "contest": "9",
            },
            callback=self.parse_mixed,
        )

    def parse_starters(self, response):
        data = list(response.json()["data"].values())[0]
        for [
            _bib,
            _number2,
            _team,
            name1,
            name2,
            _byear1,
            _byear2,
            _gender1,
            _gender2,
        ] in data:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted(map(fixName, [name1, name2])),
            )

    def handle_results(self, data, category):
        for team, entry in data.items():
            duration = self.fixDuration(team.split("///")[-1])
            names = sorted(map(lambda record: fixName(record[2]), entry))

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                type="OPA",
                category=category,
                duration=duration,
                names=names,
                bib=None,
            )

    def parse(self, response):
        data = response.json()

        yield from self.handle_results(data["data"]["#1_Männlich"], "M")
        yield from self.handle_results(data["data"]["#2_Weiblich"], "W")

    def parse_mixed(self, response):
        data = response.json()

        yield from self.handle_results(data["data"], "X")


def fixName(name):
    if "," in name:
        return " ".join(reversed(list(map(str.strip, name.split(",")))))

    return re.sub(
        r"(([A-ZÄÜÖäüöß]+[-\s])?([A-ZÄÜÖäüöß]+))\s(.+)",
        lambda match: " ".join(
            [
                match.group(4),
                "".join(
                    map(
                        lambda str: str[0] + str[1:].lower(),
                        filter(None, match.group(2, 3)),
                    )
                ),
            ]
        ),
        name.replace(",", ""),
    )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("Wetzel, Denise", "Denise Wetzel"),
        ("Julia, Keller", "Keller Julia"),
        ("TESCHNER-JEIKOWSKI Sarah", "Sarah Teschner-Jeikowski"),
        ("RAJDA Remigiusz Eugeniusz", "Remigiusz Eugeniusz Rajda"),
    ],
)
def test_fixName(input, output):
    assert fixName(input) == output
