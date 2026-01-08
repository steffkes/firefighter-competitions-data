from util import Spider, ParticipantItem, ResultItem, ResultRankItem, SlotItem
import scrapy
import re


class CompetitionSpider(Spider):
    name = __name__

    race_id = "368654"
    race_key = "196b45c8a53bf1640e5b1e4250844ea4"

    @staticmethod
    def fixName(name):
        if not name:
            return ""

        return re.sub(
            r"(([A-ZÄÜÖß]+[-\s])?([A-ZÄÜÖß]+))\s(.+)",
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
            name,
        )

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Teilnehmerlisten_RaceResult|Online-Teilnehmerliste",
                "contest": "2",
            },
            callback=self.parse_starters,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRRegStart/data/config" % self.race_id,
            callback=self.parse_slots,
        )

    def parse_slots(self, response):
        yield SlotItem(
            competition_id=self.competition_id,
            amount=response.json()["RegistrationConfig"]["Registrations"][0][
                "Contests"
            ][1]["SlotsLeft"],
        )

    def parse_starters(self, response):
        for [_bib, __id1, raw_name, _gender, _origin, _team] in response.json()["data"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName(raw_name)],
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [
        ("HARTMANN Jörg", "Jörg Hartmann"),
        ("MÜLLER Naomi", "Naomi Müller"),
        ("KNIE Nicola Simon", "Nicola Simon Knie"),
        ("WEIßHAAR Philipp", "Philipp Weißhaar"),
        (None, ""),
    ],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
