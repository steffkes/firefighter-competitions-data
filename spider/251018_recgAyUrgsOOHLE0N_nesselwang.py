from util import Spider, ParticipantItem, ResultItem, ResultRankItem, SlotItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__
    race_id = "343456"
    race_key = "5000127584775368d57fd92079d088b8"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRRegStart/data/config" % self.race_id,
            callback=self.parse_slots,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "02_Teilnehmerlisten|Teilnehmer_Einzel",
                "contest": "1",
            },
            callback=self.parse_starters_single,
        )

        yield scrapy.FormRequest(
            method="GET",
            url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "02_Teilnehmerlisten|Teilnehmer_Staffel",
                "contest": "2",
            },
            callback=self.parse_starters_relay,
        )

    def parse_slots(self, response):
        yield SlotItem(
            competition_id=self.competition_id,
            amount=response.json()["RegistrationConfig"]["Registrations"][0][
                "SlotsLeft"
            ],
        )

    def parse_starters_single(self, response):
        for [_bib, _id, name, _team] in response.json()["data"]:
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted([name]),
            )

    def parse_starters_relay(self, response):
        for [[_bib, _id, name_1, name_2]] in (response.json()["data"] or {}).values():
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=sorted([name_1, name_2]),
            )


import pytest


@pytest.mark.parametrize(
    "input,output",
    [],
)
def test_fixName(input, output):
    assert CompetitionSpider.fixName(input) == output
