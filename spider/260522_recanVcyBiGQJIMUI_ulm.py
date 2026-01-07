from util import Spider, ParticipantItem, ResultItem, ResultRankItem, SlotItem
import scrapy


class CompetitionSpider(Spider):
    name = __name__

    race_id = "368654"
    race_key = "196b45c8a53bf1640e5b1e4250844ea4"

    def start_requests(self):
        yield scrapy.FormRequest(
            method="GET",
            # url="https://my.raceresult.com/%s/RRPublish/data/list" % self.race_id,
            url="https://my.raceresult.com/%s/RRRegStart/data/config" % self.race_id,
            formdata={
                "key": self.race_key,
                "listname": "01_Teilnehmerlisten_RaceResult|Online-Teilnehmerliste",
                "contest": "1",
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
        for record in range(
            161
            - response.json()["RegistrationConfig"]["Registrations"][0]["Contests"][1][
                "SlotsLeft"
            ]
        ):
            yield ParticipantItem(
                competition_id=self.competition_id,
                names=[self.fixName(None)],
            )
