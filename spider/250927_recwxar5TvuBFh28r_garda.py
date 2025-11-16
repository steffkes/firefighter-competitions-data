from util import Spider, ParticipantItem, ResultItem, ResultRankItem
import scrapy
import re

nameMappings = {"Hindelang Günther": "Günther Hindelang"}


class CompetitionSpider(Spider):
    name = __name__

    ranks = {"category": {}}

    @staticmethod
    def fixName(name):
        [firstname, lastname] = reversed(
            list(map(lambda str: str.strip(), name.split("\xa0")))
        )

        fixed = " ".join(
            [
                firstname,
                re.sub(
                    r"^(.)(.+)$",
                    lambda match: "%s%s" % (match.group(1), match.group(2).lower()),
                    lastname,
                ),
            ]
        )

        return nameMappings.get(fixed, fixed)

    @staticmethod
    def fixDuration(raw_duration):
        if raw_duration == "Squalificato":
            return None

        return Spider.fixDuration(raw_duration)

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://gtsport.it/wp-content/glive-results/30972-revision-v1/GARDA%20LIFT%20ON%20FIRE.clax",
        )

    def parse(self, response):
        entries = dict(
            map(
                lambda entry: (entry.attrib["d"], entry),
                response.css("Engages E"),
            )
        )

        for result in response.css("Resultats R"):
            entry = entries[result.attrib["d"]]

            duration = self.fixDuration(result.attrib["t"])
            bib = result.attrib["d"]
            category = {"M": "M", "F": "W"}.get(entry.attrib["x"])

            if not duration:
                continue

            rank_total = self.ranks.get("total", 1)
            rank_category = self.ranks["category"].get(category, 1)

            yield ResultItem(
                date=self.race_date,
                competition_id=self.competition_id,
                duration=duration,
                type="MPA",
                category=category,
                names=[self.fixName(entry.attrib["n"])],
                rank=ResultRankItem(total=rank_total, category=rank_category),
                bib=bib,
            )

            self.ranks["total"] = rank_total + 1
            self.ranks["category"][category] = rank_category + 1


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("00h07'23,4", "00:07:23.4"),
        ("Squalificato", None),
    ],
)
def test_fixDuration(input, output):
    assert CompetitionSpider.fixDuration(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("KOCH Petra", "Petra Koch"),
        ("FICILI Orso Mario Bartolomeo", "Orso Mario Bartolomeo Ficili"),
        ("WEISS Anne-Kathrin", "Anne-Kathrin Weiss"),
        ("GÜNTHER Hindelang", "Günther Hindelang"),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
